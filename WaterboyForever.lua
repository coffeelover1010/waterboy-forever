local frame = CreateFrame("Frame")
local classes = { MAGE=true, PRIEST=true, WARLOCK=true, DRUID=true, SHAMAN=true, PALADIN=true, HUNTER=true }
-- Classic conjured food and water. Required level and stack size come from the client.
local water = { [5350]=1, [2288]=2, [2136]=3, [3772]=4, [8077]=5, [8078]=6, [8079]=7 }
local food = { [5349]=1, [1113]=2, [1114]=3, [1487]=4, [8075]=5, [8076]=6, [22895]=7 }
local active, attempted, generation = false, false, 0
local function Say(message)
    print("Waterboy Forever: " .. message)
end

local function Offer()
    if not active or attempted or not WaterTradeForeverDB.enabled then return end
    if not TradeFrame or not TradeFrame:IsShown() or InCombatLockdown() or GetCursorInfo() then return end
    if not UnitIsPlayer("NPC") then return end
    local _, class = UnitClass("NPC")
    local level = UnitLevel("NPC")
    local wantsFood = class == "HUNTER" or class == "WARRIOR" or class == "ROGUE"
    if (not classes[class] and not wantsFood) or not level or level < 1 then return end
    -- Never add to a trade that the player has already populated.
    for slot = 1, 6 do
        if GetTradePlayerItemInfo(slot) then attempted = true; return end
    end
    local best, waiting, candidates = {}, false, {}
    for bag = 0, NUM_BAG_SLOTS or 4 do
        for slot = 1, C_Container.GetContainerNumSlots(bag) do
            local info = C_Container.GetContainerItemInfo(bag, slot)
            local kind = info and ((classes[class] and water[info.itemID] and "water") or (wantsFood and food[info.itemID] and "food"))
            local rank = kind and (kind == "water" and water[info.itemID] or food[info.itemID])
            if rank then
                local name, link, _, _, requiredLevel, _, _, maxStack = C_Item.GetItemInfo(info.itemID)
                if not name or not requiredLevel or not maxStack then
                    waiting = true
                    C_Item.RequestLoadItemDataByID(info.itemID)
                elseif requiredLevel <= level and info.stackCount and info.stackCount > 0 and not info.isBound then
                    if info.isLocked then waiting = true
                    else
                        local item = { bag=bag, slot=slot, rank=rank, id=info.itemID, link=link or name, count=info.stackCount, maxStack=maxStack }
                        candidates[#candidates + 1] = item
                        if not best[kind] or rank > best[kind].rank or (rank == best[kind].rank and item.count > best[kind].count) then
                            best[kind] = item
                        end
                    end
                end
            end
        end
    end
    if waiting or not next(best) then return end
    -- Consolidate only the chosen rank, one move per retry so bag locks can settle.
    -- Offer at most one stack per type, or all remaining items if there are fewer.
    for _, kind in ipairs({"water", "food"}) do
        local item = best[kind]
        if item and item.count < item.maxStack then
            for _, donor in ipairs(candidates) do
                if donor ~= item and donor.id == item.id then
                    local count = math.min(donor.count, item.maxStack - item.count)
                    local ok = pcall(function()
                        if count == donor.count then
                            C_Container.PickupContainerItem(donor.bag, donor.slot)
                        else
                            C_Container.SplitContainerItem(donor.bag, donor.slot, count)
                        end
                        local cursorKind, id = GetCursorInfo()
                        if cursorKind == "item" and id == item.id then
                            C_Container.PickupContainerItem(item.bag, item.slot)
                        end
                    end)
                    local cursorKind, id = GetCursorInfo()
                    if cursorKind == "item" and id == item.id then ClearCursor() end
                    if not ok then
                        attempted = true
                        Say("Could not combine " .. kind .. ". Add it manually for this trade.")
                    end
                    return
                end
            end
        end
    end
    -- Set before touching the cursor: item events must never repeat the offer.
    attempted = true
    local tradeSlot = 1
    for _, kind in ipairs({"water", "food"}) do
        local item = best[kind]
        if item then
            if not active or not TradeFrame:IsShown() or InCombatLockdown() or GetCursorInfo() then return end
            local ok = pcall(function()
                C_Container.PickupContainerItem(item.bag, item.slot)
                local cursorKind, id = GetCursorInfo()
                if cursorKind == "item" and id == item.id then ClickTradeButton(tradeSlot) end
            end)
            local cursorKind, id = GetCursorInfo()
            if cursorKind == "item" and id == item.id then ClearCursor() end
            if not ok then
                Say("Could not offer " .. kind .. ". Add it manually for this trade.")
                return
            end
            tradeSlot = tradeSlot + 1
        end
    end
end

frame:RegisterEvent("ADDON_LOADED")
frame:RegisterEvent("TRADE_SHOW")
frame:RegisterEvent("TRADE_CLOSED")
frame:RegisterEvent("TRADE_ACCEPT_UPDATE")
frame:SetScript("OnEvent", function(_, event, name, acceptedOther)
    if event == "ADDON_LOADED" and name == "WaterboyForever" then
        if type(WaterTradeForeverDB) ~= "table" then WaterTradeForeverDB = {} end
        if WaterTradeForeverDB.enabled == nil then WaterTradeForeverDB.enabled = true end
    elseif event == "TRADE_SHOW" then
        active, attempted = true, false
        generation = generation + 1
        local token = generation
        -- Bounded retries accommodate delayed NPC identity, item cache and bag locks.
        for tick = 1, 40 do
            C_Timer.After(tick * 0.25, function()
                if token == generation then Offer() end
            end)
        end
    elseif event == "TRADE_CLOSED" then
        active = false
        generation = generation + 1
    elseif event == "TRADE_ACCEPT_UPDATE" and (name == 1 or acceptedOther == 1) then
        attempted = true
    end
end)

SLASH_WATERTRADEFOREVER1 = "/waterboy"
SLASH_WATERTRADEFOREVER2 = "/watertrade"
SlashCmdList.WATERTRADEFOREVER = function(message)
    message = (message or ""):lower():match("^%s*(.-)%s*$")
    if message == "on" then WaterTradeForeverDB.enabled = true
    elseif message == "off" then WaterTradeForeverDB.enabled = false
    end
    Say((WaterTradeForeverDB.enabled and "On" or "Off") .. ". Offers water to mana classes, food and water to hunters, and food to warriors and rogues; you click Trade. /waterboy on or off.")
end

