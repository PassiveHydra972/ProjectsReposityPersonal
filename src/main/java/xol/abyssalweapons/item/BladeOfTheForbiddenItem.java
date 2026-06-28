package xol.abyssalweapons.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.effect.MobEffectInstance;
import net.minecraft.world.effect.MobEffects;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Tiers;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import xol.abyssalweapons.entity.WardenBlastProjectile;
import xol.abyssalweapons.init.EntityInit;

/**
 * Blade of the Forbidden — 45 true dmg.
 * On hit: inflicts Wither III (3 s) and Blindness (5 s) on the target.
 * Right-click: fire 3 forbidden bolts at full WardenBlast power (30 s cooldown).
 */
public class BladeOfTheForbiddenItem extends TrueDamageSword {

    public BladeOfTheForbiddenItem() {
        super(Tiers.NETHERITE, 45.0f, 1.1f, new Item.Properties().stacksTo(1));
    }

    @Override
    public void postTrueDamageHit(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        target.addEffect(new MobEffectInstance(MobEffects.WITHER,    60, 2));  // Wither III, 3 s
        target.addEffect(new MobEffectInstance(MobEffects.BLINDNESS, 100, 0)); // Blindness, 5 s
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        if (player.getCooldowns().isOnCooldown(this)) {
            return InteractionResultHolder.pass(player.getItemInHand(hand));
        }
        if (!level.isClientSide) {
            Vec3 look = player.getLookAngle();
            for (int i = 0; i < 3; i++) {
                WardenBlastProjectile bolt = new WardenBlastProjectile(EntityInit.WARDEN_BLAST.get(), level, player);
                double spread = 0.08;
                double dx = look.x + (level.random.nextDouble() - 0.5) * spread;
                double dy = look.y + (level.random.nextDouble() - 0.5) * spread;
                double dz = look.z + (level.random.nextDouble() - 0.5) * spread;
                bolt.shoot(dx, dy, dz, 3.5f, 0.0f);
                level.addFreshEntity(bolt);
            }
            player.getCooldowns().addCooldown(this, 600); // 30 s
            player.displayClientMessage(Component.literal("\u00a74\u00bb Forbidden power unleashed! \u00ab"), true);
        }
        return InteractionResultHolder.sidedSuccess(player.getItemInHand(hand), level.isClientSide);
    }
}
