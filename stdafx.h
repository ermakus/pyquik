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

