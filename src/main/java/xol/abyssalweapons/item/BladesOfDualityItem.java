package xol.abyssalweapons.item;

import net.minecraft.network.chat.Component;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tiers;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;

import java.util.ArrayList;
import java.util.List;

/**
 * Blades of Duality — right-click strips all negative effects from the holder
 * and transfers them to every LivingEntity within 8 blocks (10 s cooldown).
 */
public class BladesOfDualityItem extends SwordItem {

    public BladesOfDualityItem() {
        super(Tiers.NETHERITE, new Item.Properties()
                .stacksTo(1)
                .attributes(SwordItem.createAttributes(Tiers.NETHERITE, 35, -2.4f)));  // 40 dmg
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        if (player.getCooldowns().isOnCooldown(this)) {
            return InteractionResultHolder.pass(player.getItemInHand(hand));
        }
        if (!level.isClientSide) {
            // Collect negative effects from the player
            List<MobEffectInstance> toTransfer = new ArrayList<>();
            for (MobEffectInstance effect : player.getActiveEffects()) {
                if (!effect.getEffect().value().isBeneficial()) {
                    toTransfer.add(new MobEffectInstance(effect));
                }
            }

            if (!toTransfer.isEmpty()) {
                // Remove from player
                for (MobEffectInstance effect : toTransfer) {
                    player.removeEffect(effect.getEffect());
                }

                // Transfer to all nearby living entities within 8 blocks
                AABB area = player.getBoundingBox().inflate(8.0);
                List<LivingEntity> nearby = level.getEntitiesOfClass(LivingEntity.class, area, e -> e != player);
                for (LivingEntity entity : nearby) {
                    for (MobEffectInstance effect : toTransfer) {
                        entity.addEffect(new MobEffectInstance(effect));
                    }
                }

                level.playSound(null, player.blockPosition(), SoundEvents.WARDEN_SONIC_CHARGE,
                        SoundSource.PLAYERS, 1.0f, 0.8f);
                player.displayClientMessage(
                        Component.literal("\u00a7b\u00bb Duality inverted \u2014 curses transferred \u00ab"), true);
            } else {
                player.displayClientMessage(
                        Component.literal("\u00a77No negative effects to transfer."), true);
            }
            player.getCooldowns().addCooldown(this, 200); // 10 s
        }
        return InteractionResultHolder.sidedSuccess(player.getItemInHand(hand), level.isClientSide);
    }
}
