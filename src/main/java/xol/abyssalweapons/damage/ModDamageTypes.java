package xol.abyssalweapons.damage;

import net.minecraft.core.Holder;
import net.minecraft.core.registries.Registries;
import net.minecraft.resources.ResourceKey;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.damagesource.DamageSource;
import net.minecraft.world.damagesource.DamageType;
import net.minecraft.world.entity.Entity;
import net.minecraft.world.level.Level;
import xol.abyssalweapons.AbyssalWeapons;

import javax.annotation.Nullable;

public final class ModDamageTypes {

    /** Key for the bypass-armour damage type used by TrueDamageSwords */
    public static final ResourceKey<DamageType> TRUE_BLADE = ResourceKey.create(
            Registries.DAMAGE_TYPE,
            ResourceLocation.fromNamespaceAndPath(AbyssalWeapons.MOD_ID, "true_blade"));

    private ModDamageTypes() {}

    /** Creates a DamageSource that bypasses armour (backed by the true_blade DamageType). */
    public static DamageSource trueBlade(Level level, @Nullable Entity directEntity, @Nullable Entity causingEntity) {
        Holder<DamageType> holder =
                level.registryAccess().registryOrThrow(Registries.DAMAGE_TYPE).getHolderOrThrow(TRUE_BLADE);
        return new DamageSource(holder, directEntity, causingEntity);
    }
}