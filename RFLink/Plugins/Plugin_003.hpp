#ifndef PLUGIN_003_H
#define PLUGIN_003_H

#include <Arduino.h>

#define PLUGIN_DESC_003 "Kaku / AB400D / Impuls / PT2262 / Sartano / Tristate"

bool Plugin_003(byte, const char*);
bool PluginTX_003(byte, const char*);
void Arc_Send(unsigned long);
void NArc_Send(unsigned long);
void TriState_Send(unsigned long);

#endif // PLUGIN_003_H