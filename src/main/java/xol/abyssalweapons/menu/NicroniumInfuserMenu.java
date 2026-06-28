package xol.abyssalweapons.menu;

import net.minecraft.world.Container;
import net.minecraft.world.SimpleContainer;
import net.minecraft.world.entity.player.Inventory;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.inventory.AbstractContainerMenu;
import net.minecraft.world.inventory.ContainerData;
import net.minecraft.world.inventory.SimpleContainerData;
import net.minecraft.world.inventory.Slot;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Items;
import xol.abyssalweapons.block.entity.NicroniumInfuserBlockEntity;
import xol.abyssalweapons.init.MenuInit;

public class NicroniumInfuserMenu extends AbstractContainerMenu {

    private final Container container;
    private final ContainerData data;

    /** Client-side constructor (called via MenuType factory). */
    public NicroniumInfuserMenu(int id, Inventory playerInv) {
        this(id, playerInv, new SimpleContainer(4), new SimpleContainerData(4));
    }

    /** Server-side constructor (called from BlockEntity). */
    public NicroniumInfuserMenu(int id, Inventory playerInv, Container container, ContainerData data) {
        super(MenuInit.NICRONIUM_INFUSER_MENU.get(), id);
        this.container = container;
        this.data = data;

        // Infuser slots  (GUI-relative x, y)
        this.addSlot(new Slot(container, NicroniumInfuserBlockEntity.SLOT_INPUT_1, 44, 35));
        this.addSlot(new Slot(container, NicroniumInfuserBlockEntity.SLOT_INPUT_2, 80, 35));
        this.addSlot(new OutputSlot(container, NicroniumInfuserBlockEntity.SLOT_OUTPUT,  134, 35));
        this.addSlot(new LavaSlot  (container, NicroniumInfuserBlockEntity.SLOT_LAVA,      8, 35));

        // Player inventory (3 rows)
        for (int row = 0; row < 3; row++) {
            for (int col = 0; col < 9; col++) {
                this.addSlot(new Slot(playerInv, col + row * 9 + 9, 8 + col * 18, 84 + row * 18));
            }
        }
        // Hotbar
        for (int col = 0; col < 9; col++) {
            this.addSlot(new Slot(playerInv, col, 8 + col * 18, 142));
        }

        this.addDataSlots(data);
    }

    // ---- Data getters (used by the screen) ----
    public int getProgress()        { return data.get(0); }
    public int getMaxProgress()     { return data.get(1); }
    public int getScaledEnergy()    { return data.get(2); }   // 0-1000
    public int getScaledMaxEnergy() { return data.get(3); }   // 1000

    @Override
    public ItemStack quickMoveStack(Player player, int index) {
        Slot slot = this.slots.get(index);
        if (!slot.hasItem()) return ItemStack.EMPTY;

        ItemStack stack = slot.getItem();
        ItemStack copy  = stack.copy();

        if (index < 4) {
            // From infuser → player inventory
            if (!this.moveItemStackTo(stack, 4, this.slots.size(), true)) return ItemStack.EMPTY;
        } else {
            // From player inventory → infuser slots
            if (stack.is(Items.LAVA_BUCKET)) {
                if (!this.moveItemStackTo(stack, 3, 4, false))
                    if (!this.moveItemStackTo(stack, 0, 2, false)) return ItemStack.EMPTY;
            } else {
                if (!this.moveItemStackTo(stack, 0, 2, false)) return ItemStack.EMPTY;
            }
        }

        if (stack.isEmpty()) slot.set(ItemStack.EMPTY);
        else slot.setChanged();

        return copy;
    }

    @Override
    public boolean stillValid(Player player) {
        return container.stillValid(player);
    }

    /** Output slot: take-only. */
    private static class OutputSlot extends Slot {
        public OutputSlot(Container container, int index, int x, int y) { super(container, index, x, y); }
        @Override public boolean mayPlace(ItemStack stack) { return false; }
    }

    /** Lava slot: only accepts lava buckets. */
    private static class LavaSlot extends Slot {
        public LavaSlot(Container container, int index, int x, int y) { super(container, index, x, y); }
        @Override public boolean mayPlace(ItemStack stack) { return stack.is(Items.LAVA_BUCKET); }
    }
}