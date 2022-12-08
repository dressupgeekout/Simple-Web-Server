cmake_minimum_required(VERSION 3.0)

project(Simple-Web-Server)

option(USE_STANDALONE_ASIO "set ON to use standalone Asio instead of Boost.Asio" OFF)
if(CMAKE_SOURCE_DIR STREQUAL "${CMAKE_CURRENT_SOURCE_DIR}")
    option(BUILD_TESTING "set ON to build library tests" ON)
else()
    option(BUILD_TESTING "set ON to build library tests" OFF)
endif()
option(BUILD_EXAMPLES "set ON to build examples" ON)
option(BUILD_FUZZING "set ON to build library fuzzers" OFF)
option(USE_OPENSSL "set OFF to build without OpenSSL" ON)

add_library(simple-web-server INTERFACE)

target_include_directories(simple-web-server INTERFACE
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}>
    $<INSTALL_INTERFACE:include>)

find_package(Threads REQUIRED)
target_link_libraries(simple-web-server INTERFACE Threads::Threads)

# TODO 2020 when Debian Jessie LTS ends:
# Remove Boost system, thread, regex components; use Boost::<component> aliases; remove Boost target_include_directories
if(USE_STANDALONE_ASIO)
    target_compile_definitions(simple-web-server INTERFACE ASIO_STANDALONE)
    find_path(ASIO_PATH asio.hpp)
    if(NOT ASIO_PATH)
        message(FATAL_ERROR "Standalone Asio not found")
    else()
        target_include_directories(simple-web-server INTERFACE ${ASIO_PATH})
    endif()
else()
    find_package(Boost 1.53.0 COMPONENTS system thread REQUIRED)
    target_link_libraries(simple-web-server INTERFACE Boost::system Boost::thread)
    if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" AND CMAKE_CXX_COMPILER_VERSION VERSION_LESS 4.9)
        target_compile_definitions(simple-web-server INTERFACE USE_BOOST_REGEX)
        find_package(Boost 1.53.0 COMPONENTS regex REQUIRED)
        target_link_libraries(simple-web-server INTERFACE Boost::regex)
    endif()
endif()
if(WIN32)
    target_link_libraries(simple-web-server INTERFACE ws2_32 wsock32)
endif()

if(APPLE)
    if(EXISTS /usr/local/opt/openssl)
        set(OPENSSL_ROOT_DIR /usr/local/opt/openssl)
    elseif(EXISTS /opt/homebrew/opt/openssl)
        set(OPENSSL_ROOT_DIR /opt/homebrew/opt/openssl)
    endif()
endif()
if(USE_OPENSSL)
    find_package(OpenSSL REQUIRED)
    target_compile_definitions(simple-web-server INTERFACE HAVE_OPENSSL)
    target_link_libraries(simple-web-server INTERFACE OpenSSL::Crypto OpenSSL::SSL)
endif()

# If Simple-Web-Server is not a sub-project:
if(CMAKE_SOURCE_DIR STREQUAL "${CMAKE_CURRENT_SOURCE_DIR}")
    if(NOT MSVC)
        add_compile_options(-std=c++11 -Wall -Wextra)
        if (CMAKE_CXX_COMPILER_ID MATCHES "Clang")
            add_compile_options(-Wthread-safety)
        endif()
    else()
        add_compile_options(/W1)
    endif()

    if(BUILD_EXAMPLES)
        find_package(Boost 1.53.0 COMPONENTS system thread filesystem REQUIRED)
        add_executable(http_examples http_examples.cpp)
        target_link_libraries(http_examples PRIVATE simple-web-server)
        target_link_libraries(http_examples PRIVATE Boost::system Boost::thread Boost::filesystem)
        if(USE_OPENSSL)
            add_executable(https_examples https_examples.cpp)
            target_link_libraries(https_examples PRIVATE simple-web-server)
            target_link_libraries(https_examples PRIVATE Boost::system Boost::thread Boost::filesystem)
        endif()
    endif()

    install(FILES asio_compatibility.hpp server_http.hpp client_http.hpp server_https.hpp client_https.hpp crypto.hpp utility.hpp status_code.hpp mutex.hpp DESTINATION include/simple-web-server)

    configure_file("cmake/${PROJECT_NAME}Config.cmake.in"
        "${PROJECT_NAME}Config.cmake" @ONLY)
    install(FILES "${CMAKE_CURRENT_BINARY_DIR}/${PROJECT_NAME}Config.cmake"
        DESTINATION share/simple-web-server)

    install(TARGETS simple-web-server EXPORT "${PROJECT_NAME}Targets")
    install(EXPORT "${PROJECT_NAME}Targets"
        DESTINATION share/simple-web-server
        NAMESPACE "${PROJECT_NAME}::")
endif()

if(BUILD_TESTING OR BUILD_FUZZING)
    if(BUILD_TESTING)
        enable_testing()
    endif()
    add_subdirectory(tests)
endif()
