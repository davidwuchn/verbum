cmake_minimum_required(VERSION 3.14)
project(vsm_tap CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Pristine attachment: link llama.cpp's built PUBLIC dylibs directly + include its
# PUBLIC headers. llama.cpp is built (not installed) at ${LLAMA_CPP_DIR}/build and
# is NOT modified. (find_package(llama) from the build tree assumes an installed
# prefix and mis-resolves include dirs, so we link by path.)
if(NOT DEFINED LLAMA_CPP_DIR)
  set(LLAMA_CPP_DIR "$ENV{HOME}/src/llama.cpp")
endif()
set(LLAMA_BIN "${LLAMA_CPP_DIR}/build/bin")

add_executable(vsm_tap vsm_tap.cpp)

target_include_directories(vsm_tap PRIVATE
  "${LLAMA_CPP_DIR}/include"
  "${LLAMA_CPP_DIR}/ggml/include")

target_link_libraries(vsm_tap PRIVATE
  "${LLAMA_BIN}/libllama.dylib"
  "${LLAMA_BIN}/libggml.dylib"
  "${LLAMA_BIN}/libggml-base.dylib")

set_target_properties(vsm_tap PROPERTIES
  BUILD_RPATH   "${LLAMA_BIN}"
  INSTALL_RPATH "${LLAMA_BIN}")
