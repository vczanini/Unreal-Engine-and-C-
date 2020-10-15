#include <iostream>
#include <ctime>

void Image()
{   std::cout << "\n               )         O_._._._A_._._._O         /(" << std::endl;
    std::cout << "                `--.___,'=================`.___,--'/" << std::endl;
    std::cout << "                 `--._.__                 __._,--'/" << std::endl;
    std::cout << "                     ,. l`~~~~~~~~~~~~~~~'l ,.  /" << std::endl;
    std::cout << "       __            ||(_)!_!_!_.-._!_!_!(_)||/            __" << std::endl;
    std::cout << "       `-.__        ||_|____!!_|;|_!!____|_||        __,-'//" << std::endl;
    std::cout << "            `==---='-----------'='-----------`=---=='    //" << std::endl;
    std::cout << "        | `--.                                         ,--' |" << std::endl;
    std::cout << "           ,.`~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~',.  /" << std::endl;
    std::cout << "           ||  ____,-------._,-------._,-------.____  ||/" << std::endl;
    std::cout << "            |||___!`=======!`=======!`=======!___|/||" << std::endl;
    std::cout << "            || |---||--------||-| | |-!!--------||---| ||" << std::endl;
    std::cout << "  __O_____O_ll_lO_____O_____O|| |'|'| ||O_____O_____Ol_ll_O_____O__" << std::endl;
    std::cout << "  o H o o H o o H o o H o o |-----------| o o H o o H o o H o o H o" << std::endl;
    std::cout << " ___H_____H_____H_____H____O =========== O____H_____H_____H_____H___" << std::endl;
    std::cout << "                          /|=============| " << std::endl;
    std::cout << "()______()______()______() '==== +-+ ====' ()______()______()______()" << std::endl;
    std::cout << "||{_}{_}||{_}{_}||{_}{_}/| ===== |_| ===== |{_}{_}||{_}{_}||{_}{_}||" << std::endl;
    std::cout << "||      ||      ||     / |==== s(   )s ====|      ||      ||      ||" << std::endl;
    std::cout << "======================()  =================  ()======================" << std::endl;
    std::cout << "----------------------/| ------------------- | ----------------------" << std::endl;
    std::cout << "                     / |---------------------|   " << std::endl;
    std::cout << "-'--'--'           ()  '---------------------'  ()" << std::endl;
    std::cout << "                   /| ------------------------- |    --'--'--'" << std::endl;
    std::cout << "       --'--'     / |---------------------------|    '--'" << std::endl;
    std::cout << "                ()  |___________________________|  ()           '--'-" << std::endl;
    std::cout << "  --'-          /| _____________________________| " << std::endl;
    std::cout << " --' gpyy      / |______________________________| " << std::endl << std::endl;
}
void Introduction(int Diff)
{
    std::cout << "Wellcome foreign, to the gate number " << Diff << "  of the temple of salazar" << std::endl;
    std::cout << "You may pass, if you know the password to unlock the gates...\n" << std::endl;
}

bool Play(int Diff)
{
    Image();
    Introduction(Diff);

    int x = rand() % (Diff + 2);
    int y = rand() % (Diff + 2);
    int z = rand() % (Diff + 2);
    int Sum = x + y + z;
    int Product = x*y*z;
    int Guess1, Guess2, Guess3, GuessSum, GuessProduct;

    std::cout << "There are 3 numbers\n";
    std::cout << "They add-up to: " << Sum;
    std::cout << "\nThey multiplies to: " << Product;
    std::cout << "\nTell me the the 3 numbers: ";
    std::cin >> Guess1 >> Guess2 >> Guess3;

    GuessSum = Guess1 + Guess2 + Guess3;
    GuessProduct = Guess1 * Guess2 * Guess3;

    if (GuessSum == Sum && GuessProduct == Product)
    {
        std::cout << ("You can pass this gate now, go foward to the next one\n\n");
        return true;
    }
    else
    {
        std::cout << ("That's not the code they give to you\n\n");
        return false;
    }
}

int main()
{
    srand(time(NULL)); // Randomize the seed based on the time of the day
    int LevelDiff = 1;
    int const Max = 3;

    while (LevelDiff <= Max)
    {
        bool bLevelComp = Play(LevelDiff);
        std::cin.clear();
        std::cin.ignore();

        if (bLevelComp)
        {
            LevelDiff++;
        }
        
    }
    std::cout << "Congratulations, you can enter the temple now";
    return 0;
}