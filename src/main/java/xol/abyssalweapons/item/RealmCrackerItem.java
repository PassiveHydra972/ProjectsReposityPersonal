package xol.abyssalweapons.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Tiers;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;

import java.util.List;

/**
 * Realm Cracker — 75 true dmg.
 * Right-click: all living entities within 12 blocks are teleported 20 blocks upward (30 s cooldown).
 */
public class RealmCrackerItem extends TrueDamageSword {

    public RealmCrackerItem() {
        super(Tiers.NETHERITE, 75.0f, 0.7f, new Item.Properties().stacksTo(1));
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        if (player.getCooldowns().isOnCooldown(this)) {
            return InteractionResultHolder.pass(player.getItemInHand(hand));
        }
        if (!level.isClientSide) {
            AABB area = player.getBoundingBox().inflate(12.0);
            List<LivingEntity> nearby = level.getEntitiesOfClass(LivingEntity.class, area, e -> e != player);
            for (LivingEntity entity : nearby) {
                entity.teleportTo(entity.getX(), entity.getY() + 20.0, entity.getZ());
            }
            player.getCooldowns().addCooldown(this, 600); // 30 s
            player.displayClientMessage(Component.literal(
                    "\u00a75\u00bb Realm cracked! " + nearby.size() + " enemies launched! \u00ab"), true);
        }
        return InteractionResultHolder.sidedSuccess(player.getItemInHand(hand), level.isClientSide);
    }
}
