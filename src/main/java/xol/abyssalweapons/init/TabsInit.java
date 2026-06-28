package xol.abyssalweapons.init;

import net.minecraft.core.registries.Registries;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.CreativeModeTab;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import xol.abyssalweapons.AbyssalWeapons;

public class TabsInit {

    public static final DeferredRegister<CreativeModeTab> TABS =
            DeferredRegister.create(Registries.CREATIVE_MODE_TAB, AbyssalWeapons.MOD_ID);

    public static final DeferredHolder<CreativeModeTab, CreativeModeTab> MAIN_TAB =
            TABS.register("main_tab", () -> CreativeModeTab.builder()
                    .title(Component.translatable("itemGroup.abyssalweapons.main"))
                    .icon(() -> ItemInit.MULTIVERSAL_BLADE.get().getDefaultInstance())
                    .displayItems((params, output) -> {
                        // Original Weapons
                        output.accept(ItemInit.MULTIVERSAL_BLADE.get());
                        output.accept(ItemInit.MOONGLOW_BLADE.get());
                        output.accept(ItemInit.HOLOSABER.get());
                        output.accept(ItemInit.REINFORCED_BLADE.get());
                        output.accept(ItemInit.BLADE_OF_ETERNITY_ASCENDUM.get());
                        output.accept(ItemInit.BLADES_OF_DUALITY.get());
                        output.accept(ItemInit.SWORD_OF_SELECTION.get());
                        output.accept(ItemInit.BLADE_OF_THE_DEAD.get());
                        output.accept(ItemInit.SWORD_OF_REVERBERANCE.get());
                        output.accept(ItemInit.ASTRAL_BASTION.get());
                        // 2.0 Weapons
                        output.accept(ItemInit.LASER_BLADE.get());
                        output.accept(ItemInit.DUELING_SWORD_DULL.get());
                        output.accept(ItemInit.DUELING_SWORD_SHARP.get());
                        output.accept(ItemInit.DUELING_SWORD_RAZOR.get());
                        output.accept(ItemInit.PHANTOM_BLADE.get());
                        output.accept(ItemInit.HEXBREAKER.get());
                        output.accept(ItemInit.RAPIER_OF_REVENGE.get());
                        output.accept(ItemInit.BLADE_OF_THE_CONQUEROR.get());
                        output.accept(ItemInit.SABER_CLAW.get());
                        output.accept(ItemInit.BLADE_OF_THE_FORBIDDEN.get());
                        output.accept(ItemInit.BLADES_OF_CONVERGENCE.get());
                        output.accept(ItemInit.WORLD_SPLITTER.get());
                        output.accept(ItemInit.THE_APEX.get());
                        output.accept(ItemInit.RAZOR_OF_INFINITY.get());
                        output.accept(ItemInit.REALM_CRACKER.get());
                        output.accept(ItemInit.LOST_BLADES_OF_INFINITY.get());
                        // 2.0 Shields
                        output.accept(ItemInit.MIRROR_SHIELD.get());
                        output.accept(ItemInit.SERPENTINE_SHIELD.get());
                        // 2.0 Bows
                        output.accept(ItemInit.ELEMENTIUM_BOW_MK1.get());
                        output.accept(ItemInit.ELEMENTIUM_BOW_MK2.get());
                        output.accept(ItemInit.ELEMENTIUM_BOW_MK3.get());
                        // Original Materials
                        output.accept(ItemInit.DARKSTEEL_SHEETS.get());
                        output.accept(ItemInit.IONITE_ALLOY.get());
                        output.accept(ItemInit.MALICIUM_ALLOY.get());
                        output.accept(ItemInit.HAUNTED_ALLOY.get());
                        output.accept(ItemInit.POLARIUM_ALLOY.get());
                        output.accept(ItemInit.EMBERIUM_ALLOY.get());
                        output.accept(ItemInit.HEAT_SINGULARITY.get());
                        // 2.0 Alloys
                        output.accept(ItemInit.ASTRALLIUM_ALLOY.get());
                        output.accept(ItemInit.CRYSTONIUM_ALLOY.get());
                        output.accept(ItemInit.HEXTORIUM_ALLOY.get());
                        output.accept(ItemInit.VELLORIUM_ALLOY.get());
                        output.accept(ItemInit.INCADIUM_ALLOY.get());
                        // Blocks
                        output.accept(ItemInit.DARKSTEEL_BLOCK_ITEM.get());
                        output.accept(ItemInit.SINGULARITY_CORE_ITEM.get());
                        output.accept(ItemInit.NICRONIUM_INFUSER_ITEM.get());
                    })
                    .build());
}
