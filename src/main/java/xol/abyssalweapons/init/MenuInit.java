package xol.abyssalweapons.init;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.flag.FeatureFlags;
import net.minecraft.world.inventory.MenuType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import xol.abyssalweapons.AbyssalWeapons;
import xol.abyssalweapons.menu.NicroniumInfuserMenu;

public class MenuInit {

    public static final DeferredRegister<MenuType<?>> MENUS =
            DeferredRegister.create(Registries.MENU, AbyssalWeapons.MOD_ID);

    public static final DeferredHolder<MenuType<?>, MenuType<NicroniumInfuserMenu>> NICRONIUM_INFUSER_MENU =
            MENUS.register("nicronium_infuser", () ->
                    new MenuType<>((id, inv) -> new NicroniumInfuserMenu(id, inv), FeatureFlags.DEFAULT_FLAGS));
}
