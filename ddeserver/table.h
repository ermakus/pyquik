#pragma once

#include <string>
#include <vector>

using std::string;
using std::vector;

template<typename T> 
class TableData : public vector< vector< T > > {

public:
	DWORD rows;
	DWORD cols;
	
	TableData() : rows(0), cols(0) {
	}

	void init(DWORD r, DWORD c, const T& s) {
		assign(r, std::vector< T >(c,s));
		rows = r;
		cols = c;
	}

	void reset() {
		this->clear();
		rows = cols = 0;
	}
};

typedef TableData<string> TableDataString;
typedef TableData<double> TableDataDouble;

