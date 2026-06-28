package xol.abyssalweapons.init;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.entity.EntityType;
import net.minecraft.world.entity.MobCategory;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import xol.abyssalweapons.AbyssalWeapons;
import xol.abyssalweapons.entity.WardenBlastProjectile;

public class EntityInit {

    public static final DeferredRegister<EntityType<?>> ENTITY_TYPES =
            DeferredRegister.create(Registries.ENTITY_TYPE, AbyssalWeapons.MOD_ID);

    public static final DeferredHolder<EntityType<?>, EntityType<WardenBlastProjectile>> WARDEN_BLAST =
            ENTITY_TYPES.register("warden_blast", () ->
                    EntityType.Builder.<WardenBlastProjectile>of(WardenBlastProjectile::new, MobCategory.MISC)
                            .sized(0.3f, 0.3f)
                            .clientTrackingRange(64)
                            .build("abyssalweapons:warden_blast"));
}