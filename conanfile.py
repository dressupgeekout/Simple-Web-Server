from conans import ConanFile, CMake, tools

class SimpleWebServerConan(ConanFile):
    name = "Simple-Web-Server"
    version = "3.1.1"
    license = "https://gitlab.com/eidheim/Simple-Web-Server/-/blob/master/LICENSE"
    author = "Ole Christian Eidheim"
    url = "https://gitlab.com/eidheim/Simple-Web-Server"
    description = "A very simple, fast, multithreaded, platform independent HTTP and HTTPS server and client library implemented using C++11 and Boost.Asio. Created to be an easy way to make REST resources available from C++ applications."
    options = {"openssl": [True, False]}
    default_options = {"openssl": True}
    requires = "boost/[>=1.53.0]" 
    generators = "cmake"
    src_path = "."
    exports_sources = "*"    

    def config_options(self):
        if self.options.openssl:
            self.requires("openssl/1.1.1k")

    def package_id(self):
        self.info.header_only()
        
    def package(self):
        self.copy("*.h", dst="include", src=self.src_path)
        self.copy("*.hpp", dst="include", src=self.src_path)
        self.copy("LICENSE", dst="licenses", src=self.src_path)

    def package_info(self):
        self.cpp_info.libs = ["simple-web-server"]
