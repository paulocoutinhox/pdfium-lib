cmake_minimum_required(VERSION 3.24)
project(sample)

# sources
file(GLOB S_FILES_PROJECT "src/*.cpp")

if(UNIX AND NOT APPLE)
    file(GLOB H_FILES_PDFIUM "../build/linux/release/include/*.h")
elseif(WIN32)
    file(GLOB H_FILES_PDFIUM "../build/windows/release/include/*.h")
    add_definitions(-DWIN32)    
elseif(APPLE)
    file(GLOB H_FILES_PDFIUM "../build/macos/release/include/*.h")
endif()

set(
    PROJ_FILES
    ${S_FILES_PROJECT}
    ${H_FILES_PDFIUM}
)

# frameworks
if(UNIX AND APPLE)
    find_library(FWK_CORE_GRAPHICS CoreGraphics)
    find_library(FWK_FOUNDATION Foundation)
    find_library(FWK_SECURITY Security)
endif()

# target
add_executable(${PROJECT_NAME} ${PROJ_FILES})

# links
if(WIN32)
    add_library(pdfium SHARED IMPORTED)
else()
    target_link_libraries(${PROJECT_NAME} PRIVATE "pdfium")
endif()

if(UNIX AND APPLE)
    target_link_libraries(${PROJECT_NAME} PRIVATE ${FWK_FOUNDATION})
    target_link_libraries(${PROJECT_NAME} PRIVATE ${FWK_CORE_GRAPHICS})
    target_link_libraries(${PROJECT_NAME} PRIVATE ${FWK_SECURITY})
endif()

# paths
if(UNIX AND NOT APPLE)
    target_link_directories(${PROJECT_NAME} PRIVATE "../build/linux/release/lib/x64")
    target_include_directories(${PROJECT_NAME} PRIVATE "../build/linux/release/include")
elseif(WIN32)
    target_link_directories(${PROJECT_NAME} PRIVATE "../build/windows/release/lib/x64")
    target_include_directories(${PROJECT_NAME} PRIVATE "../build/windows/release/include")
elseif(APPLE)
    target_link_directories(${PROJECT_NAME} PRIVATE "../build/macos/release/lib")
    target_include_directories(${PROJECT_NAME} PRIVATE "../build/macos/release/include")
endif()
