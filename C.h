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
#include "Surface.h"
#include "Rays.h"
#include "RayC.h"
#include "SurfaceClass.h"
#include "Client.generated.h"



UCLASS( ClassGroup=(Test), meta=(BlueprintSpawnableComponent) )
class MYPROJECT_API UClient : public UActorComponent
{
	GENERATED_BODY()

public:	
	// Sets default values for this component's properties
	UClient();
  
protected:
	// Called when the game starts
	virtual void BeginPlay() override;

	

public:	
	// Called every frame
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	zmq::message_t msg;

	zmq::message_t msgRay;

	zmq::message_t msgGlobal;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	TArray<FRelativeSurface> RSurf;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	TArray<FGlobalSurface> Global;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	TArray<FRayPoint> rp;
	
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	TArray<FRayPoint> Ray;

	UFUNCTION(BlueprintCallable, Category = "AA")
	FString fPrintFSurface(TArray<FRelativeSurf> g);

	UFUNCTION(BlueprintCallable, Category = "AA")
	FString fPrintFGlobalSurface(TArray<FGlobalSurf> gg);

	UFUNCTION(BlueprintCallable, Category = "AA")
	FString fPrintFGetRays(TArray<FRayP> r);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	TArray<FRayP> Ray2;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	TArray<FRayP> RP2;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	TArray<FRelativeSurf> RSurface;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AA")
	TArray<FGlobalSurf> GlobalSurface;


	UFUNCTION(BlueprintCallable, Category = "AA")
	void LoadRelativeSurface();

	UFUNCTION(BlueprintCallable, Category = "AA")
	void LoadGlobalSurface();
	
	UFUNCTION(BlueprintCallable, Category = "AA")
	void LoadRays();

	UFUNCTION(BlueprintCallable, Category = "AA")
	void CallGlobal();

	UFUNCTION(BlueprintCallable, Category = "AA")
	void CallSurface();

	UFUNCTION(BlueprintCallable, Category = "AA")
	void CallRay();
};