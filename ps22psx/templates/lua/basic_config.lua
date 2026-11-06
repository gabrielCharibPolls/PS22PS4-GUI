-- Example LUA patch template
local eeObj = getEEObject()
local emuObj = getEmuObject()

local patcher = function()
  -- eeObj.WriteMem32(0x00100000, 0x00000000)
end

emuObj.AddVsyncHook(patcher)
