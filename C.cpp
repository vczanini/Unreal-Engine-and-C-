// Fill out your copyright notice in the Description page of Project Settings.

#include "Client.h"
#include <zmq.hpp>
#include <zmq_addon.hpp>
#include "JsonObject.h"
#include "Json.h"
#include "Dom/JsonValue.h"
#include "Runtime/JsonUtilities/Public/JsonObjectConverter.h"
#include "Serialization/JsonSerializer.h"
#include "JsonUtilities.h"
#include "string"
#include "Surface.h"
#include "Rays.h"
#include "RayC.h"
#include "SurfaceClass.h"
#include "DelayAction.h"

// Sets default values for this component's properties
UClient::UClient()
{
	// Set this component to be initialized when the game starts, and to be ticked every frame.  You can turn these features
	// off to improve performance if you don't need them.
	PrimaryComponentTick.bCanEverTick = true;

	// ...
}


// Called when the game starts
void UClient::BeginPlay()
{
	Super::BeginPlay();
	zmq::context_t context;
	zmq::socket_t socket(context, zmq::socket_type::dealer);
	socket.connect("tcp://45.56.102.215:5573");

	zmq::multipart_t SendSystem("cmd LoadSystem 600602.DBS");
	get.SendSystem(socket);



}

// Called every frame
void UClient::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	// ...
}

FString UClient::fPrintFSurface(TArray<FRelativeSurf> g)
{
	FString printed = "";
	for(int32 i = 0; i < g.Num(); i++)
	{
		printed += g[i].typeCode + " \r";
		printed += FString::SanitizeFloat(g[i].curvature) + "  ";
		printed += FString::SanitizeFloat(g[i].distToNext) + "  ";
		printed += FString::SanitizeFloat(g[i].refrIndex) + "   ";
		printed += FString::SanitizeFloat(g[i].glassCode) + "   ";
		printed += FString::SanitizeFloat(g[i].ySemiAperture) + "   \n";
	}
	return printed;
}

FString UClient::fPrintFGlobalSurface(TArray<FGlobalSurf> gg)
{
	FString printed = "";
	for(int32 i = 0; i < gg.Num(); i++)
	{
		printed += FString::FromInt(gg[i].surfaceNumber) + "  ";
		printed += gg[i].typeCode + " \r";
		printed += FString::SanitizeFloat(gg[i].XXX) + "   ";
		printed += FString::SanitizeFloat(gg[i].YYY) + "   ";
		printed += FString::SanitizeFloat(gg[i].ZZZ) + "   ";
		printed += FString::SanitizeFloat(gg[i].ISX) + "   ";
		printed += FString::SanitizeFloat(gg[i].ISY) + "   ";
		printed += FString::SanitizeFloat(gg[i].ISZ) + "   ";
		printed += FString::SanitizeFloat(gg[i].JSX) + "   ";
		printed += FString::SanitizeFloat(gg[i].JSY) + "   ";
		printed += FString::SanitizeFloat(gg[i].JSZ) + "   ";
		printed += FString::SanitizeFloat(gg[i].KSX) + "   ";
		printed += FString::SanitizeFloat(gg[i].KSY) + "   ";
		printed += FString::SanitizeFloat(gg[i].KSZ) + "   \n";

		
	}
	return printed;
}

FString UClient::fPrintFGetRays(TArray<FRayP> r)
{
	FString printed = "";
	for(int32 i = 0; i < r.Num(); i++)
	{
		printed += FString::SanitizeFloat(r[i].XPos) + "   ";
		printed += FString::SanitizeFloat(r[i].YPos) + "   ";
		printed += FString::SanitizeFloat(r[i].ZPos) + "  \n";
	}
	return printed;
}

void UClient::LoadRelativeSurface()
{
	//Convert to the USTRUCT
	TSharedRef<TJsonReader<TCHAR>> JSonReader = TJsonReaderFactory<>::Create(UTF8_TO_TCHAR(msg.data()));
	TArray<TSharedPtr<FJsonValue>> JsonObject;
	FJsonSerializer::Deserialize(JSonReader, JsonObject);
	FJsonObjectConverter::JsonArrayToUStruct<FRelativeSurf>(JsonObject, &RSurface, 0, 0);
}

void UClient::LoadGlobalSurface()
{

	//Convert to the USTRUCT
	TSharedRef<TJsonReader<TCHAR>> JSonReaderGlobal = TJsonReaderFactory<>::Create(UTF8_TO_TCHAR(glob.data()));
	TArray<TSharedPtr<FJsonValue>> JsonObjectGlobal;
	if(FJsonSerializer::Deserialize(JSonReaderGlobal, JsonObjectGlobal))
	{
		UE_LOG(LogTemp, Warning, TEXT("worked"));
	}
	FJsonObjectConverter::JsonArrayToUStruct<FGlobalSurf>(JsonObjectGlobal, &GlobalSurface, 0, 0);
}

void UClient::LoadRays()
{
	//Convert to the USTRUCT
	TSharedRef<TJsonReader<TCHAR>> JSonReaderRay = TJsonReaderFactory<>::Create(UTF8_TO_TCHAR(msgRay.data()));
	TArray<TSharedPtr<FJsonValue>> JsonObjectListofLists;
	FJsonSerializer::Deserialize(JSonReaderRay, JsonObjectListofLists);
	for(int32 k = 0; k < JsonObjectListofLists.Num(); k++)
	{
		TArray<TSharedPtr<FJsonValue>> JsonObjectList = JsonObjectListofLists[k]->AsArray();
		FJsonObjectConverter::JsonArrayToUStruct<FRayP>(JsonObjectList, &RP2, 0, 0);
		Ray2 += RP2;
	}
}

void UClient::CallGlobal()
{
	zmq::context_t context;
	zmq::socket_t socket(context, zmq::socket_type::dealer);
	socket.connect("tcp://45.56.102.215:5573");

	//Send the global surface message
	zmq::multipart_t sndGlobal("cmd GetSurfacesGlobal 0 0");
	sndGlobal.send(socket);
	
	socket.recv(&msgGlobal);
}

void UClient::CallSurface()
{
	zmq::context_t context;
	zmq::socket_t socket(context, zmq::socket_type::dealer);
	socket.connect("tcp://45.56.102.215:5573");

	//Send the surface message
	zmq::multipart_t snd("cmd GetSurfaces 0");
	snd.send(socket);

	//Receive the surface message
	socket.recv(&msg);
}

void UClient::CallRay()
{
	zmq::context_t context;
	zmq::socket_t socket(context, zmq::socket_type::dealer);
	socket.connect("tcp://45.56.102.215:5573");

	//Send the Ray message
	zmq::multipart_t sndRay("cmd GetRays 0 2 3");
	sndRay.send(socket);

	//Receive the Ray message
	socket.recv(&msgRay);
}