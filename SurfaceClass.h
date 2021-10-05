// Fill out your copyright notice in the Description page of Project Settings.

#pragma once

#include <zmq_addon.hpp>
#include <zmq.hpp>
#include"Json.h"
#include "JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include"Runtime/JsonUtilities/Public/JsonObjectConverter.h"
#include "Dom/JsonValue.h"
#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SurfaceClass.generated.h"

USTRUCT(BlueprintType)
struct FRelativeSurf
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	FString typeCode;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	float curvature;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	float distToNext;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	float refrIndex;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	float glassCode;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	float ySemiAperture;
};

USTRUCT(BlueprintType)
struct FGlobalSurf
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	int32 surfaceNumber;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	FString typeCode;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	float XXX;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	float YYY;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	float ZZZ;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	float ISX;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	float ISY;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	float ISZ;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	float JSX;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	float JSY;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	float JSZ;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	float KSX;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	float KSY;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
    float KSZ;
};

UCLASS( ClassGroup=(Custom), meta=(BlueprintSpawnableComponent) )
class MYPROJECT_API USurfaceClass : public UActorComponent
{
	GENERATED_BODY()

public:	
	// Sets default values for this component's properties
	USurfaceClass();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	TArray<FRelativeSurf> RSurface;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	TArray<FGlobalSurf> GlobalSurface;

	UFUNCTION(BlueprintCallable, Category = "AA")
	void GetVariables(TArray<FRelativeSurf> S, TArray<FGlobalSurf> G);

protected:
	// Called when the game starts
	virtual void BeginPlay() override;

public:	
	// Called every frame
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

		
};
