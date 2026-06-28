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
 * World Splitter — 40 true dmg.
 * Right-click: shockwave blast — all living entities within 8 blocks take 25% of their max HP
 * as sonic damage (bypasses armour) and are launched straight up (15 s cooldown).
 */
public class WorldSplitterItem extends TrueDamageSword {

    public WorldSplitterItem() {
        super(Tiers.NETHERITE, 40.0f, 0.8f, new Item.Properties().stacksTo(1));
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        if (player.getCooldowns().isOnCooldown(this)) {
            return InteractionResultHolder.pass(player.getItemInHand(hand));
        }
        if (!level.isClientSide) {
            AABB area = player.getBoundingBox().inflate(8.0);
            List<LivingEntity> nearby = level.getEntitiesOfClass(LivingEntity.class, area, e -> e != player);
            for (LivingEntity entity : nearby) {
                float damage = entity.getMaxHealth() * 0.25f;
                entity.hurt(level.damageSources().sonicBoom(player), damage);
                // Launch upward
                entity.setDeltaMovement(entity.getDeltaMovement().x, 1.5, entity.getDeltaMovement().z);
            }
            player.getCooldowns().addCooldown(this, 300); // 15 s
            player.displayClientMessage(Component.literal("\u00a7c\u00bb World shattered! \u00ab"), true);
        }
        return InteractionResultHolder.sidedSuccess(player.getItemInHand(hand), level.isClientSide);
    }
}
