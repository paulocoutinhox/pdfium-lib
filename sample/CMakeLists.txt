cmake_minimum_required(VERSION 3.24)
project(sample)

# sources
file(GLOB S_FILES_PROJECT "src/*.cpp")
file(GLOB H_FILES_PDFIUM "../build/macos/release/include/*.h")

set(
    PROJ_FILES
    ${S_FILES_PROJECT}
    ${H_FILES_PDFIUM}
)

# frameworks
find_library(FWK_CORE_GRAPHICS CoreGraphics)
find_library(FWK_FOUNDATION Foundation)
find_library(FWK_SECURITY Security)

# target
add_executable(${PROJECT_NAME} ${PROJ_FILES})

# links
target_link_libraries(${PROJECT_NAME} PRIVATE "pdfium")

target_link_libraries(${PROJECT_NAME} PRIVATE ${FWK_FOUNDATION})
target_link_libraries(${PROJECT_NAME} PRIVATE ${FWK_CORE_GRAPHICS})
target_link_libraries(${PROJECT_NAME} PRIVATE ${FWK_SECURITY})

# paths
target_link_directories(${PROJECT_NAME} PRIVATE "../build/macos/release/lib")
target_include_directories(${PROJECT_NAME} PRIVATE "../build/macos/release/include")
