package xol.abyssalweapons.init;

import net.minecraft.core.registries.Registries;
import net.minecraft.world.level.block.entity.BlockEntityType;
import net.neoforged.neoforge.registries.DeferredHolder;
import net.neoforged.neoforge.registries.DeferredRegister;
import xol.abyssalweapons.AbyssalWeapons;
import xol.abyssalweapons.block.entity.NicroniumInfuserBlockEntity;

public class BlockEntityInit {

    public static final DeferredRegister<BlockEntityType<?>> BLOCK_ENTITIES =
            DeferredRegister.create(Registries.BLOCK_ENTITY_TYPE, AbyssalWeapons.MOD_ID);

    public static final DeferredHolder<BlockEntityType<?>, BlockEntityType<NicroniumInfuserBlockEntity>> NICRONIUM_INFUSER_BE =
            BLOCK_ENTITIES.register("nicronium_infuser", () ->
                    BlockEntityType.Builder.of(NicroniumInfuserBlockEntity::new,
                            BlockInit.NICRONIUM_INFUSER.get()).build(null));
}
