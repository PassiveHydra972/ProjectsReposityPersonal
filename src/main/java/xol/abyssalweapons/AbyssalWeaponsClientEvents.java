package xol.abyssalweapons;

import net.minecraft.ChatFormatting;
import net.minecraft.network.chat.Component;
import net.minecraft.world.item.Item;
import net.neoforged.api.distmarker.Dist;
import net.neoforged.bus.api.SubscribeEvent;
import net.neoforged.fml.common.EventBusSubscriber;
import net.neoforged.neoforge.event.entity.player.ItemTooltipEvent;
import xol.abyssalweapons.init.ItemInit;

@EventBusSubscriber(modid = AbyssalWeapons.MOD_ID, bus = EventBusSubscriber.Bus.GAME, value = Dist.CLIENT)
public class AbyssalWeaponsClientEvents {

    @SubscribeEvent
    public static void onItemTooltip(ItemTooltipEvent event) {
        Item item = event.getItemStack().getItem();

        // ── Original weapons ─────────────────────────────────────────────────
        if (item == ItemInit.MULTIVERSAL_BLADE.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.multiversal_blade").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.MOONGLOW_BLADE.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.moonglow_blade").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.HOLOSABER.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.holosaber").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.REINFORCED_BLADE.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.reinforced_blade").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.BLADE_OF_ETERNITY_ASCENDUM.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.blade_of_eternity_ascendum").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.BLADES_OF_DUALITY.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.bladesofduality").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.SWORD_OF_SELECTION.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.sword_of_selection").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.BLADE_OF_THE_DEAD.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.blade_of_the_dead").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.SWORD_OF_REVERBERANCE.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.sword_of_reverberance").withStyle(ChatFormatting.GRAY));
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.sword_of_reverberance.passive").withStyle(ChatFormatting.DARK_PURPLE));
        } else if (item == ItemInit.ASTRAL_BASTION.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.astral_bastion").withStyle(ChatFormatting.AQUA));
        // ── 2.0 weapons ──────────────────────────────────────────────────────
        } else if (item == ItemInit.LASER_BLADE.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.laser_blade").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.DUELING_SWORD_DULL.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.dueling_sword_dull").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.DUELING_SWORD_SHARP.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.dueling_sword_sharp").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.DUELING_SWORD_RAZOR.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.dueling_sword_razor_edged").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.PHANTOM_BLADE.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.phantom_blade").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.HEXBREAKER.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.hexbreaker").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.RAPIER_OF_REVENGE.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.rapier_of_revenge").withStyle(ChatFormatting.GRAY));
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.rapier_of_revenge.passive").withStyle(ChatFormatting.DARK_PURPLE));
        } else if (item == ItemInit.BLADE_OF_THE_CONQUEROR.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.blade_of_the_conqueror").withStyle(ChatFormatting.GRAY));
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.blade_of_the_conqueror.passive").withStyle(ChatFormatting.GOLD));
        } else if (item == ItemInit.SABER_CLAW.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.saber_claw").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.BLADE_OF_THE_FORBIDDEN.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.blade_of_the_forbidden").withStyle(ChatFormatting.GRAY));
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.blade_of_the_forbidden.passive").withStyle(ChatFormatting.DARK_RED));
        } else if (item == ItemInit.BLADES_OF_CONVERGENCE.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.blades_of_convergence").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.WORLD_SPLITTER.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.world_splitter").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.THE_APEX.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.the_apex").withStyle(ChatFormatting.GRAY));
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.the_apex.passive").withStyle(ChatFormatting.GOLD));
        } else if (item == ItemInit.RAZOR_OF_INFINITY.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.razor_of_infinity").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.REALM_CRACKER.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.realm_cracker").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.LOST_BLADES_OF_INFINITY.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.lost_blades_of_infinity").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.MIRROR_SHIELD.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.mirror_shield").withStyle(ChatFormatting.AQUA));
        } else if (item == ItemInit.SERPENTINE_SHIELD.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.serpentine_shield").withStyle(ChatFormatting.GREEN));
        } else if (item == ItemInit.ELEMENTIUM_BOW_MK1.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.elementium_bow_mk1").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.ELEMENTIUM_BOW_MK2.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.elementium_bow_mk2").withStyle(ChatFormatting.GRAY));
        } else if (item == ItemInit.ELEMENTIUM_BOW_MK3.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.elementium_bow_mk3").withStyle(ChatFormatting.GRAY));
        // ── Alloys ───────────────────────────────────────────────────────────
        } else if (item == ItemInit.IONITE_ALLOY.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.ionite_alloy").withStyle(ChatFormatting.YELLOW));
        } else if (item == ItemInit.MALICIUM_ALLOY.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.malicium_alloy").withStyle(ChatFormatting.YELLOW));
        } else if (item == ItemInit.HAUNTED_ALLOY.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.haunted_alloy").withStyle(ChatFormatting.YELLOW));
        } else if (item == ItemInit.POLARIUM_ALLOY.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.polarium_alloy").withStyle(ChatFormatting.YELLOW));
        } else if (item == ItemInit.EMBERIUM_ALLOY.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.emberium_alloy").withStyle(ChatFormatting.YELLOW));
        } else if (item == ItemInit.ASTRALLIUM_ALLOY.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.astrallium_alloy").withStyle(ChatFormatting.YELLOW));
        } else if (item == ItemInit.CRYSTONIUM_ALLOY.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.crystonium_alloy").withStyle(ChatFormatting.YELLOW));
        } else if (item == ItemInit.HEXTORIUM_ALLOY.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.hextorium_alloy").withStyle(ChatFormatting.YELLOW));
        } else if (item == ItemInit.VELLORIUM_ALLOY.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.vellorium_alloy").withStyle(ChatFormatting.YELLOW));
        } else if (item == ItemInit.INCADIUM_ALLOY.get()) {
            event.getToolTip().add(Component.translatable("tooltip.abyssalweapons.incadium_alloy").withStyle(ChatFormatting.YELLOW));
        }
    }
}
