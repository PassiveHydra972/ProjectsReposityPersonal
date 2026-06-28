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
import net.minecraft.world.item.Tiers;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.AABB;
import net.minecraft.world.phys.Vec3;
import xol.abyssalweapons.entity.WardenBlastProjectile;
import xol.abyssalweapons.init.EntityInit;

import java.util.ArrayList;
import java.util.List;

/**
 * Blades of Convergence — 55 true dmg. Upgraded Blades of Duality.
 * Right-click: strips ALL effects (positive + negative) from the player,
 * transfers all negative effects to every enemy within 10 blocks,
 * and fires 8 convergence blasts (10 s cooldown).
 */
public class BladesOfConvergenceItem extends TrueDamageSword {

    public BladesOfConvergenceItem() {
        super(Tiers.NETHERITE, 55.0f, 1.3f, new Item.Properties().stacksTo(1));
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        if (player.getCooldowns().isOnCooldown(this)) {
            return InteractionResultHolder.pass(player.getItemInHand(hand));
        }
        if (!level.isClientSide) {
            // Collect all negative effects
            List<MobEffectInstance> negative = new ArrayList<>();
            for (MobEffectInstance effect : player.getActiveEffects()) {
                if (!effect.getEffect().value().isBeneficial()) {
                    negative.add(new MobEffectInstance(effect));
                }
            }

            // Strip ALL effects from player (positive and negative)
            player.removeAllEffects();

            // Transfer negative effects to nearby enemies
            AABB area = player.getBoundingBox().inflate(10.0);
            List<LivingEntity> nearby = level.getEntitiesOfClass(LivingEntity.class, area, e -> e != player);
            for (LivingEntity entity : nearby) {
                for (MobEffectInstance effect : negative) {
                    entity.addEffect(new MobEffectInstance(effect));
                }
            }

            // Fire 8 convergence blasts
            Vec3 look = player.getLookAngle();
            for (int i = 0; i < 8; i++) {
                WardenBlastProjectile blast = new WardenBlastProjectile(EntityInit.WARDEN_BLAST.get(), level, player);
                double spread = 0.25;
                double dx = look.x + (level.random.nextDouble() - 0.5) * spread;
                double dy = look.y + (level.random.nextDouble() - 0.5) * spread;
                double dz = look.z + (level.random.nextDouble() - 0.5) * spread;
                blast.shoot(dx, dy, dz, 3.5f, 0.0f);
                level.addFreshEntity(blast);
            }

            level.playSound(null, player.blockPosition(), SoundEvents.WARDEN_SONIC_CHARGE,
                    SoundSource.PLAYERS, 1.0f, 0.5f);
            player.getCooldowns().addCooldown(this, 200); // 10 s
            player.displayClientMessage(Component.literal("\u00a7d\u00bb Convergence! All curses repelled! \u00ab"), true);
        }
        return InteractionResultHolder.sidedSuccess(player.getItemInHand(hand), level.isClientSide);
    }
}
