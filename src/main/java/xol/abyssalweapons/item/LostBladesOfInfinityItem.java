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
 * Lost Blades of Infinity — 90 true dmg.
 * Right-click: fires 20 autonomous blades, each dealing 5% of target's max HP (30 s cooldown).
 */
public class LostBladesOfInfinityItem extends TrueDamageSword {

    public LostBladesOfInfinityItem() {
        super(Tiers.NETHERITE, 90.0f, 0.6f, new Item.Properties().stacksTo(1));
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        if (player.getCooldowns().isOnCooldown(this)) {
            return InteractionResultHolder.pass(player.getItemInHand(hand));
        }
        if (!level.isClientSide) {
            Vec3 look = player.getLookAngle();
            for (int i = 0; i < 20; i++) {
                WardenBlastProjectile blade = new WardenBlastProjectile(EntityInit.WARDEN_BLAST.get(), level, player);
                blade.damageMultiplier = 0.05f; // 5% max HP per blade
                double spread = 0.35;
                double dx = look.x + (level.random.nextDouble() - 0.5) * spread;
                double dy = look.y + (level.random.nextDouble() - 0.5) * spread;
                double dz = look.z + (level.random.nextDouble() - 0.5) * spread;
                blade.shoot(dx, dy, dz, 3.0f, 0.0f);
                level.addFreshEntity(blade);
            }
            player.getCooldowns().addCooldown(this, 600); // 30 s
            player.displayClientMessage(Component.literal("\u00a7d\u00bb INFINITE BLADES! \u00ab"), true);
        }
        return InteractionResultHolder.sidedSuccess(player.getItemInHand(hand), level.isClientSide);
    }
}
