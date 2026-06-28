package xol.abyssalweapons.init;

import com.mojang.serialization.MapCodec;
import net.neoforged.neoforge.common.loot.IGlobalLootModifier;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import net.neoforged.neoforge.registries.NeoForgeRegistries;
import xol.abyssalweapons.AbyssalWeapons;
import xol.abyssalweapons.loot.HeatSingularityBlazeModifier;

public class LootModifierInit {

    public static final DeferredRegister<MapCodec<? extends IGlobalLootModifier>> LOOT_MODIFIERS =
            DeferredRegister.create(NeoForgeRegistries.Keys.GLOBAL_LOOT_MODIFIER_SERIALIZERS, AbyssalWeapons.MOD_ID);

    public static final DeferredHolder<MapCodec<? extends IGlobalLootModifier>, MapCodec<HeatSingularityBlazeModifier>> HEAT_SINGULARITY_BLAZE =
            LOOT_MODIFIERS.register("heat_singularity_blaze", () -> HeatSingularityBlazeModifier.CODEC);
}
