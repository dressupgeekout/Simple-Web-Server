from conans import ConanFile, CMake, tools

class SimpleWebServerConan(ConanFile):
    name = "Simple-Web-Server"
    version = "2.2.0"
    license = "MIT"
    author = "Ole Christian Eidheim"
    url = "git@gitlab.com:eidheim/Simple-Web-Server.git"
    description = "A very simple, fast, multithreaded, platform independent HTTP and HTTPS server and client library implemented using C++11 and Boost.Asio. Created to be an easy way to make REST resources available from C++ applications."
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "testing": [True, False], "fuzzing": [True, False], "openssl": [True, False]}
    default_options = {"shared": False, "testing": False, "fuzzing": False, "openssl": True}
    requires = "boost/[>=1.53.0]" 
    generators = "cmake"
    src_path = "."
    exports_sources = "*"    

    def config_options(self):
        if self.options.openssl:
            self.requires("openssl/1.1.1k")

    def build(self):
        defines = {
            "BUILD_TESTING": self.options.testing,
            "BUILD_FUZZING": self.options.fuzzing,
            "USE_OPENSSL": self.options.openssl
        }

        cmake = CMake(self)
        cmake.configure(defs=defines, source_folder=self.src_path)
        cmake.build()

    def package(self):
        self.copy("*.hpp", dst="include", src=self.src_path)
        self.copy("LICENSE", dst="licenses", src=self.src_path)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["Simple-Web-Server"]
