package xol.abyssalweapons.init;

import net.minecraft.world.level.block.Block;
import net.minecraft.world.level.block.SoundType;
import net.minecraft.world.level.block.state.BlockBehaviour;
import net.minecraft.world.level.material.MapColor;
import net.neoforged.neoforge.registries.DeferredBlock;
import net.neoforged.neoforge.registries.DeferredRegister;
import xol.abyssalweapons.AbyssalWeapons;
import xol.abyssalweapons.block.NicroniumInfuserBlock;

public class BlockInit {

    public static final DeferredRegister.Blocks BLOCKS = DeferredRegister.createBlocks(AbyssalWeapons.MOD_ID);

    public static final DeferredBlock<Block> DARKSTEEL_BLOCK = BLOCKS.registerSimpleBlock("darksteel_block",
            BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_GRAY)
                    .requiresCorrectToolForDrops()
                    .strength(5.0f, 6.0f)
                    .sound(SoundType.METAL));

    public static final DeferredBlock<Block> SINGULARITY_CORE = BLOCKS.registerSimpleBlock("singularity_core",
            BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_ORANGE)
                    .requiresCorrectToolForDrops()
                    .strength(4.0f, 8.0f)
                    .lightLevel(s -> 7)
                    .sound(SoundType.METAL));

    public static final DeferredBlock<NicroniumInfuserBlock> NICRONIUM_INFUSER = BLOCKS.register("nicronium_infuser",
            () -> new NicroniumInfuserBlock(BlockBehaviour.Properties.of()
                    .mapColor(MapColor.COLOR_GRAY)
                    .requiresCorrectToolForDrops()
                    .strength(5.0f, 6.0f)
                    .sound(SoundType.METAL)));
}
