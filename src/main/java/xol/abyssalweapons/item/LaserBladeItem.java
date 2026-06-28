package xol.abyssalweapons.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tiers;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import xol.abyssalweapons.entity.WardenBlastProjectile;
import xol.abyssalweapons.init.EntityInit;

/**
 * Laser Blade — 16 dmg, right-click fires a concentrated laser bolt (10% max HP, 5 s cooldown).
 */
public class LaserBladeItem extends SwordItem {

    public LaserBladeItem() {
        super(Tiers.DIAMOND,
                new Item.Properties()
                        .stacksTo(1)
                        .attributes(SwordItem.createAttributes(Tiers.DIAMOND, 12, -2.4f))); // 16 dmg
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        if (player.getCooldowns().isOnCooldown(this)) {
            return InteractionResultHolder.pass(player.getItemInHand(hand));
        }
        if (!level.isClientSide) {
            Vec3 look = player.getLookAngle();
            WardenBlastProjectile bolt = new WardenBlastProjectile(EntityInit.WARDEN_BLAST.get(), level, player);
            bolt.damageMultiplier = 0.10f; // 10% max HP per bolt
            bolt.shoot(look.x, look.y, look.z, 4.0f, 0.0f);
            level.addFreshEntity(bolt);
            player.getCooldowns().addCooldown(this, 100); // 5 s
            player.displayClientMessage(Component.literal("\u00a7b\u00bb Laser bolt fired \u00ab"), true);
        }
        return InteractionResultHolder.sidedSuccess(player.getItemInHand(hand), level.isClientSide);
    }
}
