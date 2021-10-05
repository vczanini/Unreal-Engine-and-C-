USTRUCT(BlueprintType)
struct FRayP
{
    GENERATED_BODY()

    
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
    int32 SurfaceNumber;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
    float XPos;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
    float YPos;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
    float ZPos;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
    float RCosX;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
    float RCosY;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
    float RCosZ;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
    float NCosX;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
    float NCosY;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
    float NCosZ;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
    float n;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
    float OpAngle;
};