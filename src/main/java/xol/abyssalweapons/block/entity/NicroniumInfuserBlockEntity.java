package xol.abyssalweapons.block.entity;

import net.minecraft.core.BlockPos;
import net.minecraft.core.HolderLookup;
import net.minecraft.core.NonNullList;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.ContainerHelper;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import net.minecraft.world.level.Level;
import net.minecraft.world.level.block.entity.BaseContainerBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.neoforged.neoforge.energy.IEnergyStorage;
import xol.abyssalweapons.init.BlockEntityInit;
import xol.abyssalweapons.init.ItemInit;
import xol.abyssalweapons.menu.NicroniumInfuserMenu;

public class NicroniumInfuserBlockEntity extends BaseContainerBlockEntity {

    public static final int SLOT_INPUT_1    = 0;
    public static final int SLOT_INPUT_2    = 1;
    public static final int SLOT_OUTPUT     = 2;
    public static final int SLOT_LAVA       = 3;

    public static final int MAX_PROGRESS    = 60;
    public static final int MAX_ENERGY      = 100_000;
    public static final int ENERGY_PER_TICK = 40;
    public static final int LAVA_ENERGY     = 100_000;

    private NonNullList<ItemStack> items = NonNullList.withSize(4, ItemStack.EMPTY);
    public int progress = 0;
    public int energy   = 0;

    // Capability-exposed FE handler (receive from external FE sources; no extraction)
    public final IEnergyStorage energyStorage = new IEnergyStorage() {
        @Override public int receiveEnergy(int maxReceive, boolean simulate) {
            int toReceive = Math.min(MAX_ENERGY - energy, maxReceive);
            if (!simulate) { energy += toReceive; setChanged(); }
            return toReceive;
        }
        @Override public int extractEnergy(int maxExtract, boolean simulate) { return 0; }
        @Override public int getEnergyStored()    { return energy; }
        @Override public int getMaxEnergyStored() { return MAX_ENERGY; }
        @Override public boolean canExtract() { return false; }
        @Override public boolean canReceive() { return energy < MAX_ENERGY; }
    };

    // ContainerData syncs progress + energy (scaled /100) to the client
    public final ContainerData data = new ContainerData() {
        @Override public int get(int index) {
            return switch (index) {
                case 0 -> progress;
                case 1 -> MAX_PROGRESS;
                case 2 -> energy / 100;        // scaled 0-1000
                case 3 -> MAX_ENERGY / 100;    // 1000
                default -> 0;
            };
        }
        @Override public void set(int index, int value) {
            if (index == 0) progress = value;
            if (index == 2) energy   = value * 100;
        }
        @Override public int getCount() { return 4; }
    };

    public NicroniumInfuserBlockEntity(BlockPos pos, BlockState state) {
        super(BlockEntityInit.NICRONIUM_INFUSER_BE.get(), pos, state);
    }

    @Override protected Component getDefaultName() {
        return Component.translatable("block.abyssalweapons.nicronium_infuser");
    }
    @Override protected NonNullList<ItemStack> getItems()                          { return items; }
    @Override protected void setItems(NonNullList<ItemStack> items)                { this.items = items; }
    @Override public    int getContainerSize()                                     { return 4; }
    @Override protected AbstractContainerMenu createMenu(int id, Inventory inv)   {
        return new NicroniumInfuserMenu(id, inv, this, data);
    }

    // ==================== ALLOY RECIPES ====================
    public static ItemStack getResult(ItemStack a, ItemStack b) {
        if (a.isEmpty() || b.isEmpty()) return ItemStack.EMPTY;

        if (matches(a, b, Items.LAPIS_LAZULI,  Items.AMETHYST_SHARD))
            return new ItemStack(ItemInit.POLARIUM_ALLOY.get());
        if (matches(a, b, ItemInit.POLARIUM_ALLOY.get(), Items.NETHER_BRICK))
            return new ItemStack(ItemInit.MALICIUM_ALLOY.get());
        if (matches(a, b, ItemInit.DARKSTEEL_SHEETS.get(), Items.BLAZE_POWDER))
            return new ItemStack(ItemInit.EMBERIUM_ALLOY.get());
        if (matches(a, b, Items.SOUL_SAND, Items.BONE))
            return new ItemStack(ItemInit.HAUNTED_ALLOY.get());
        if (matches(a, b, Items.PRISMARINE_SHARD, ItemInit.POLARIUM_ALLOY.get()))
            return new ItemStack(ItemInit.IONITE_ALLOY.get());

        // ==================== TIER 2 ALLOY RECIPES (2.0) ====================
        // astrallium_alloy: polarium_alloy + nether_star  (stellar fusion)
        if (matches(a, b, ItemInit.POLARIUM_ALLOY.get(), Items.NETHER_STAR))
            return new ItemStack(ItemInit.ASTRALLIUM_ALLOY.get());
        // crystonium_alloy: ionite_alloy + quartz_block  (crystal resonance)
        if (matches(a, b, ItemInit.IONITE_ALLOY.get(), Items.QUARTZ_BLOCK))
            return new ItemStack(ItemInit.CRYSTONIUM_ALLOY.get());
        // hextorium_alloy: malicium_alloy + echo_shard  (dark resonance)
        if (matches(a, b, ItemInit.MALICIUM_ALLOY.get(), Items.ECHO_SHARD))
            return new ItemStack(ItemInit.HEXTORIUM_ALLOY.get());
        // vellorium_alloy: emberium_alloy + dragon_breath  (dragon-fire alloy)
        if (matches(a, b, ItemInit.EMBERIUM_ALLOY.get(), Items.DRAGON_BREATH))
            return new ItemStack(ItemInit.VELLORIUM_ALLOY.get());
        // incadium_alloy: haunted_alloy + blaze_rod  (soul-fire alloy)
        if (matches(a, b, ItemInit.HAUNTED_ALLOY.get(), Items.BLAZE_ROD))
            return new ItemStack(ItemInit.INCADIUM_ALLOY.get());

        return ItemStack.EMPTY;
    }

    private static boolean matches(ItemStack a, ItemStack b, Item item1, Item item2) {
        return (a.is(item1) && b.is(item2)) || (a.is(item2) && b.is(item1));
    }

    // ==================== TICK ====================
    public static void serverTick(Level level, BlockPos pos, BlockState state, NicroniumInfuserBlockEntity be) {
        // Consume lava bucket -> fill energy
        ItemStack lavaStack = be.items.get(SLOT_LAVA);
        if (lavaStack.is(Items.LAVA_BUCKET) && be.energy < MAX_ENERGY) {
            be.energy = Math.min(MAX_ENERGY, be.energy + LAVA_ENERGY);
            be.items.set(SLOT_LAVA, new ItemStack(Items.BUCKET));
            be.setChanged();
        }

        ItemStack input1 = be.items.get(SLOT_INPUT_1);
        ItemStack input2 = be.items.get(SLOT_INPUT_2);
        ItemStack output = be.items.get(SLOT_OUTPUT);
        ItemStack result = getResult(input1, input2);

        if (!result.isEmpty() && canOutput(output, result) && be.energy >= ENERGY_PER_TICK) {
            be.energy -= ENERGY_PER_TICK;
            be.progress++;
            be.setChanged();
            if (be.progress >= MAX_PROGRESS) {
                be.progress = 0;
                input1.shrink(1);
                input2.shrink(1);
                if (output.isEmpty()) {
                    be.items.set(SLOT_OUTPUT, result.copy());
                } else {
                    output.grow(1);
                }
            }
        } else if (result.isEmpty() || !canOutput(output, result)) {
            // No valid recipe or output full: reset progress
            if (be.progress > 0) {
                be.progress = 0;
                be.setChanged();
            }
        }
        // If valid recipe but no energy: pause (hold progress)
    }

    private static boolean canOutput(ItemStack current, ItemStack result) {
        return current.isEmpty()
                || (current.is(result.getItem()) && current.getCount() < current.getMaxStackSize());
    }

    // ==================== NBT ====================
    @Override
    protected void saveAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.saveAdditional(tag, registries);
        ContainerHelper.saveAllItems(tag, items, registries);
        tag.putInt("Progress", progress);
        tag.putInt("Energy",   energy);
    }

    @Override
    protected void loadAdditional(CompoundTag tag, HolderLookup.Provider registries) {
        super.loadAdditional(tag, registries);
        items    = NonNullList.withSize(getContainerSize(), ItemStack.EMPTY);
        ContainerHelper.loadAllItems(tag, items, registries);
        progress = tag.getInt("Progress");
        energy   = tag.getInt("Energy");
    }
}