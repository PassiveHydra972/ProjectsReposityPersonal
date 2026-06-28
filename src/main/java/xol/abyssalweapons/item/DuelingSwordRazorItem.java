package xol.abyssalweapons.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Tiers;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import xol.abyssalweapons.entity.WardenBlastProjectile;
import xol.abyssalweapons.init.EntityInit;

/**
 * Dueling Sword: Razor-Edged — 30 true dmg, right-click fires a razor blade bolt (12% max HP, 5 s cooldown).
 */
public class DuelingSwordRazorItem extends TrueDamageSword {

    public DuelingSwordRazorItem() {
        super(Tiers.DIAMOND, 30.0f, 1.4f, new Item.Properties().stacksTo(1));
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        if (player.getCooldowns().isOnCooldown(this)) {
            return InteractionResultHolder.pass(player.getItemInHand(hand));
        }
        if (!level.isClientSide) {
            Vec3 look = player.getLookAngle();
            WardenBlastProjectile blade = new WardenBlastProjectile(EntityInit.WARDEN_BLAST.get(), level, player);
            blade.damageMultiplier = 0.12f; // 12% max HP
            blade.shoot(look.x, look.y, look.z, 4.0f, 0.0f);
            level.addFreshEntity(blade);
            player.getCooldowns().addCooldown(this, 100); // 5 s
            player.displayClientMessage(Component.literal("\u00a77\u00bb Razor blade hurled \u00ab"), true);
        }
        return InteractionResultHolder.sidedSuccess(player.getItemInHand(hand), level.isClientSide);
    }
}
