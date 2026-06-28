package xol.abyssalweapons.client.screen;

import net.minecraft.client.gui.GuiGraphics;
import net.minecraft.client.gui.screens.inventory.AbstractContainerScreen;
import net.minecraft.network.chat.Component;
import net.minecraft.resources.ResourceLocation;
import net.minecraft.world.entity.player.Inventory;
import xol.abyssalweapons.AbyssalWeapons;
import xol.abyssalweapons.menu.NicroniumInfuserMenu;

public class NicroniumInfuserScreen extends AbstractContainerScreen<NicroniumInfuserMenu> {

    private static final ResourceLocation TEXTURE = ResourceLocation.fromNamespaceAndPath(
            AbyssalWeapons.MOD_ID, "textures/gui/nicronium_infuser.png");

    // FE bar: interior of the track the texture bakes at (7,62)-(22,74)
    private static final int FE_X = 8;
    private static final int FE_Y = 63;
    private static final int FE_W = 14;
    private static final int FE_H = 11;

    // Progress bar: interior of the track the texture bakes at (99,31)-(130,48)
    private static final int PROG_X = 100;
    private static final int PROG_Y = 32;
    private static final int PROG_W = 29;
    private static final int PROG_H = 15;

    public NicroniumInfuserScreen(NicroniumInfuserMenu menu, Inventory inv, Component title) {
        super(menu, inv, title);
        this.imageWidth  = 176;
        this.imageHeight = 166;
        this.titleLabelY = 4;
        // Note: this.font is null here — title centering is done in init()
    }

    @Override
    public void init() {
        super.init();
        // Centre the title now that this.font is available
        this.titleLabelX = (this.imageWidth - this.font.width(this.title)) / 2;
    }

    @Override
    protected void renderBg(GuiGraphics graphics, float partialTick, int mouseX, int mouseY) {
        int x = (this.width  - this.imageWidth)  / 2;
        int y = (this.height - this.imageHeight) / 2;

        // Base texture (handles slot borders, panel layout, FE/progress tracks)
        graphics.blit(TEXTURE, x, y, 0, 0, this.imageWidth, this.imageHeight);

        // ── Lava slot: orange-tinted inset ──────────────────────────────────
        graphics.fill(x + 7,  y + 34, x + 26, y + 53, 0xFF7A3300);  // outer dark orange
        graphics.fill(x + 8,  y + 35, x + 25, y + 52, 0xFF140900);  // inner near-black

        // "Fuel" label above lava slot
        graphics.drawString(this.font, "Fuel", x + 5, y + 26, 0xFF667788, false);

        // ── FE label (below lava slot, above bar track) ──────────────────────
        graphics.drawString(this.font, "FE", x + FE_X, y + 53, 0xFF4FC3F7, false);

        // ── FE fill (bottom-to-top, teal; texture draws background + border) ─
        int feX = x + FE_X;
        int feY = y + FE_Y;
        int scaled    = this.menu.getScaledEnergy();
        int scaledMax = this.menu.getScaledMaxEnergy();
        int feFilled  = scaledMax > 0 ? (scaled * FE_H / scaledMax) : 0;
        if (feFilled > 0) {
            graphics.fill(feX, feY + FE_H - feFilled, feX + FE_W, feY + FE_H, 0xFF4FC3F7);
        }

        // ── Progress fill (left-to-right, teal; texture draws background + border) ─
        int pX          = x + PROG_X;
        int pY          = y + PROG_Y;
        int progress    = this.menu.getProgress();
        int maxProgress = this.menu.getMaxProgress();
        int pFilled     = maxProgress > 0 ? (progress * PROG_W / maxProgress) : 0;
        if (pFilled > 0) {
            graphics.fill(pX, pY, pX + pFilled, pY + PROG_H, 0xFF4FC3F7);
        }
    }

    @Override
    public void render(GuiGraphics graphics, int mouseX, int mouseY, float partialTick) {
        super.render(graphics, mouseX, mouseY, partialTick);
        this.renderTooltip(graphics, mouseX, mouseY);

        int x = (this.width  - this.imageWidth)  / 2;
        int y = (this.height - this.imageHeight) / 2;

        // Tooltip: FE bar
        if (mouseX >= x + FE_X && mouseX <= x + FE_X + FE_W
         && mouseY >= y + FE_Y && mouseY <= y + FE_Y + FE_H) {
            int fe    = this.menu.getScaledEnergy()    * 100;
            int feMax = this.menu.getScaledMaxEnergy() * 100;
            graphics.renderTooltip(this.font,
                Component.literal(String.format("%,d / %,d FE", fe, feMax)),
                mouseX, mouseY);
        }

        // Tooltip: progress bar
        if (mouseX >= x + PROG_X && mouseX <= x + PROG_X + PROG_W
         && mouseY >= y + PROG_Y && mouseY <= y + PROG_Y + PROG_H) {
            int progress    = this.menu.getProgress();
            int maxProgress = this.menu.getMaxProgress();
            int pct = maxProgress > 0 ? (progress * 100 / maxProgress) : 0;
            graphics.renderTooltip(this.font,
                Component.literal(pct + "% complete"),
                mouseX, mouseY);
        }
    }
}