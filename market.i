%module(directors="1") trading

%{
#include "market.h"
%}

%feature ("director") MarketListener;

%include "market.h"

