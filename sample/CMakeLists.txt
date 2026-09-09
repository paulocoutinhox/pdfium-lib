cmake_minimum_required(VERSION 3.24)
project(sample)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Multi config generators would otherwise put the binary in a per config subfolder.
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}")

foreach(CONFIG ${CMAKE_CONFIGURATION_TYPES})
    string(TOUPPER "${CONFIG}" CONFIG_UPPER)
    set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_${CONFIG_UPPER} "${CMAKE_BINARY_DIR}")
endforeach()

# The pdfium build to link against, which decides the library directory and the runtime.
set(PDFIUM_CONFIG "release" CACHE STRING "pdfium build configuration")

# Resolves the platform directory name.
if(APPLE)
    set(PDFIUM_PLATFORM "macos")
elseif(WIN32)
    set(PDFIUM_PLATFORM "windows")
else()
    set(PDFIUM_PLATFORM "linux")
endif()

# The path is absolute because a custom command resolves a relative one against the build directory.
set(PDFIUM_DIR "${CMAKE_CURRENT_SOURCE_DIR}/../build/${PDFIUM_PLATFORM}/${PDFIUM_CONFIG}")
set(PDFIUM_INCLUDE_DIR "${PDFIUM_DIR}/include")

# A single universal library is shipped on macOS, while the other platforms keep one directory per architecture.
if(APPLE)
    set(PDFIUM_LIB_DIR "${PDFIUM_DIR}/lib")
else()
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "^(aarch64|arm64|ARM64)$")
        set(PDFIUM_ARCH "arm64")
    else()
        set(PDFIUM_ARCH "x64")
    endif()

    set(PDFIUM_LIB_DIR "${PDFIUM_DIR}/lib/${PDFIUM_ARCH}")
endif()

# Collects the sources.
file(GLOB S_FILES_PROJECT "src/*.cpp")
file(GLOB H_FILES_PDFIUM "${PDFIUM_INCLUDE_DIR}/*.h")

set(
    PROJ_FILES
    ${S_FILES_PROJECT}
    ${H_FILES_PDFIUM}
)

# Declares the executable.
add_executable(${PROJECT_NAME} ${PROJ_FILES})

# Links what each platform needs.
target_link_libraries(${PROJECT_NAME} PRIVATE "pdfium")

if(APPLE)
    find_library(FWK_CORE_GRAPHICS CoreGraphics)
    find_library(FWK_FOUNDATION Foundation)
    find_library(FWK_SECURITY Security)

    target_link_libraries(${PROJECT_NAME} PRIVATE ${FWK_FOUNDATION})
    target_link_libraries(${PROJECT_NAME} PRIVATE ${FWK_CORE_GRAPHICS})
    target_link_libraries(${PROJECT_NAME} PRIVATE ${FWK_SECURITY})
elseif(NOT WIN32)
    find_package(Threads REQUIRED)

    target_link_libraries(${PROJECT_NAME} PRIVATE Threads::Threads)
    target_link_libraries(${PROJECT_NAME} PRIVATE ${CMAKE_DL_LIBS})

    # The shared library is copied next to the executable before it runs.
    set_target_properties(${PROJECT_NAME} PROPERTIES BUILD_RPATH "$ORIGIN")
endif()

# Points the compiler and the linker at the staged library.
target_link_directories(${PROJECT_NAME} PRIVATE ${PDFIUM_LIB_DIR})
target_include_directories(${PROJECT_NAME} PRIVATE ${PDFIUM_INCLUDE_DIR})

# The platforms that link a shared library need it beside the executable to run.
if(NOT APPLE)
    set(PDFIUM_SHARED_LIBRARY "${PDFIUM_LIB_DIR}/${CMAKE_SHARED_LIBRARY_PREFIX}pdfium${CMAKE_SHARED_LIBRARY_SUFFIX}")

    add_custom_command(
        TARGET ${PROJECT_NAME}
        POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${PDFIUM_SHARED_LIBRARY}"
            "$<TARGET_FILE_DIR:${PROJECT_NAME}>"
    )
endif()
