#pragma once

#include "targetver.h"

#define WIN32_LEAN_AND_MEAN             // Exclude rarely-used stuff from Windows headers
// Windows Header Files:
#include <windows.h>

// C RunTime Header Files
#include <stdlib.h>
#include <malloc.h>
#include <memory.h>
#include <tchar.h>

#define _WTL_USE_CSTRING

#if 0
#include <atlbase.h>
#include <atlapp.h>
//#include <atlwin.h>
#include <atlmisc.h>
#else
#include <atlstr.h>
#endif

typedef CString String;
//std::string

#ifdef _DEBUG
#define DEBUG_NEW new(_NORMAL_BLOCK, __FILE__, __LINE__)
#endif

#ifdef _DEBUG
#define ASSERT(a) _ASSERT(a)
#define TRACE ATLTRACE2
#else
#define ASSERT(a) 
#define TRACE 
#endif

enum {
	UM_FIRST = WM_USER,
	UM_SERVER_FAULT,
	UM_CLIENT_MESSAGE,
	UM_PRINT_MESSAGE,
	UM_MINIMIZE,
	UM_RESTORE,
};

extern HWND GetMainWindow();

#define PRINT_MESSAGE(msg) TRACE(msg)
//SendMessage(GetMainWindow(), UM_PRINT_MESSAGE, (WPARAM)(LPCTSTR)(msg), 0);

#define SEPARATE_THREAD_TO_SEND_DATA 1

#include <string>

static std::string cp1251_to_utf8(const char *str)
{
	std::string res;	
	int result_u, result_c;


	result_u = MultiByteToWideChar(1251,
		0,
		str,
		-1,
		0,
		0);
	
	if (!result_u)
		return 0;

	wchar_t *ures = new wchar_t[result_u];

	if(!MultiByteToWideChar(1251,
		0,
		str,
		-1,
		ures,
		result_u))
	{
		delete[] ures;
		return 0;
	}


	result_c = WideCharToMultiByte(
		CP_UTF8,
		0,
		ures,
		-1,
		0,
		0,
		0, 0);

	if(!result_c)
	{
		delete [] ures;
		return 0;
	}

	char *cres = new char[result_c];

	if(!WideCharToMultiByte(
		CP_UTF8,
		0,
		ures,
		-1,
		cres,
		result_c,
		0, 0))
	{
		delete[] cres;
		return 0;
	}
	delete[] ures;
	res.append(cres);
	delete[] cres;
	return res;
}