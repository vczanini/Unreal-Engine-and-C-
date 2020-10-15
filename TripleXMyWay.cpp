#include <iostream>
#include <fstream>
#include <vector>
#include <ctime>
using namespace std;

void Image()
{
    std::fstream Input("temple.txt", std::fstream::in);
    if(Input.is_open())
    {
        char ch;
        std::vector<char> rVector;
        while(Input >> std::noskipws >> ch) 
        {
            rVector.push_back(ch);
        }
        for(auto i : rVector)
        {
            std::cout << i;
        }
        Input.close();
    }
}

void Intro(int Diff)
{

    printf("\n\nWellcome foreign, to the gate numer %d temple of salazar\n", Diff);
    printf("You may pass, if you know the password to unlock the gates...\n\n");
}

int Play(int pass, int Diff)
{
   
    int x = rand() % (Diff + 2), y = rand() % (Diff + 2), z = rand() % (Diff+2), Sum, Product, Guess1, Guess2;
    int Guess3, GuessSum, GuessProduct;

    Image();
    Intro(Diff);

    Sum = x + y + z;
    Product = x*y*z;

    printf("There are 3 numbers\n");
    printf("They add up to: %d\n", Sum);
    printf("They multiplies to: %d\n", Product);
    printf("Tell me the 3 numbers: ");
    scanf("%d %d %d", &Guess1, &Guess2, &Guess3);
    
    GuessSum = Guess1 + Guess2 + Guess3;
    GuessProduct = Guess1 * Guess2 * Guess3;

        if (GuessSum == Sum || GuessProduct == Product)
    {
        printf("You can pass the gate now, wellcome to the temple of Salazar\n");
        pass = 1;
        return pass;
    }
    else
    {
        printf("Guards!!! Kill him\n");
        pass = 0;
        return pass;
    }
}

int main()
{
    srand(time(NULL)); //Randons the seed based on daytime.
    int LevelDiff = 1, Max = 3, Pass = 0;

    while (LevelDiff <= Max)
    {
        if (Pass == 0)
        {
           Pass = Play(Pass, LevelDiff);
        }
        else
        {
            LevelDiff++;
            Pass = 0;
        }
        
    }
    printf("Congratulations, you can enter the temple now");
    return 0;
}