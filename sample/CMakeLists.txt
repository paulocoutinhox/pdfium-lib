cmake_minimum_required(VERSION 3.1)
project(sample)

file(GLOB S_FILES_PROJECT "src/*.cpp")
file(GLOB H_FILES_PDFIUM "include/*.h")

set(
    PROJ_FILES
    ${S_FILES_PROJECT}
    ${H_FILES_PDFIUM}
)

find_library(CORE_GRAPHICS_FWK CoreGraphics)
get_filename_component(FRAMEWORK_DIR ${CORE_GRAPHICS_FWK} PATH)

set(LIBS pdfium)
link_directories("../build/macos/release/")

add_executable(sample ${PROJ_FILES})

set_target_properties(sample PROPERTIES
    LINK_FLAGS "-F ${FRAMEWORK_DIR}"
)

target_link_libraries(sample ${LIBS})
target_link_libraries(sample "-framework CoreGraphics")
target_link_libraries(sample "-framework Foundation")

target_include_directories(sample PRIVATE "include")