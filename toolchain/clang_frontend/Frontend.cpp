// I must get inside. - Arbiter

int clang_main(int Argc, char** Argv);
extern "C" int __declspec(dllexport) ninja_frontend(int Argc, char** Argv)
{
    return clang_main(Argc, Argv);
}
