package xol.abyssalweapons.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tiers;

/**
 * Phantom Blade — 20 dmg. On hit: 40% chance to teleport the enemy 5 blocks upward,
 * forcing them to take fall damage when they land.
 */
public class PhantomBladeItem extends SwordItem {

    public PhantomBladeItem() {
        super(Tiers.DIAMOND,
                new Item.Properties()
                        .stacksTo(1)
                        .attributes(SwordItem.createAttributes(Tiers.DIAMOND, 16, -2.4f))); // 20 dmg
    }

    @Override
    public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        boolean result = super.hurtEnemy(stack, target, attacker);
        if (result && !attacker.level().isClientSide) {
            if (attacker.getRandom().nextFloat() < 0.40f) {
                // Teleport target 5 blocks upward — they will take fall damage on landing
                target.teleportTo(target.getX(), target.getY() + 5.0, target.getZ());
                if (attacker instanceof Player player) {
                    player.displayClientMessage(Component.literal("\u00a75\u00bb Phantom phase! \u00ab"), true);
                }
            }
        }
        return result;
    }
}
