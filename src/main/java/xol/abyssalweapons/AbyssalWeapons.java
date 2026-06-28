package xol.abyssalweapons;

import net.neoforged.bus.api.IEventBus;
import net.neoforged.fml.common.Mod;
import net.neoforged.neoforge.capabilities.Capabilities;
import net.neoforged.neoforge.capabilities.RegisterCapabilitiesEvent;
import xol.abyssalweapons.block.entity.NicroniumInfuserBlockEntity;
import xol.abyssalweapons.init.*;

@Mod(AbyssalWeapons.MOD_ID)
public class AbyssalWeapons {

    public static final String MOD_ID = "abyssalweapons";

    public AbyssalWeapons(IEventBus modEventBus) {
        ItemInit.ITEMS.register(modEventBus);
        BlockInit.BLOCKS.register(modEventBus);
        BlockEntityInit.BLOCK_ENTITIES.register(modEventBus);
        MenuInit.MENUS.register(modEventBus);
        TabsInit.TABS.register(modEventBus);
        LootModifierInit.LOOT_MODIFIERS.register(modEventBus);
        EntityInit.ENTITY_TYPES.register(modEventBus);
        modEventBus.addListener(this::onRegisterCapabilities);
    }

    private void onRegisterCapabilities(RegisterCapabilitiesEvent event) {
        event.registerBlockEntity(
            Capabilities.EnergyStorage.BLOCK,
            BlockEntityInit.NICRONIUM_INFUSER_BE.get(),
            (be, side) -> be.energyStorage);
    }
}
