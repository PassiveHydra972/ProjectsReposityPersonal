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

/** Multiversal Greatsword Of Eternal Damnation — 65 true dmg / speed 0.9 / right-click: 5 warden blasts (10 s cooldown) */
public class MultiversalGreatsword extends TrueDamageSword {

    public MultiversalGreatsword() {
        super(Tiers.NETHERITE, 65.0f, 0.9f, new Item.Properties().stacksTo(1));
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        if (player.getCooldowns().isOnCooldown(this)) {
            return InteractionResultHolder.pass(player.getItemInHand(hand));
        }
        if (!level.isClientSide) {
            Vec3 look = player.getLookAngle();
            for (int i = 0; i < 15; i++) {
                WardenBlastProjectile blast = new WardenBlastProjectile(EntityInit.WARDEN_BLAST.get(), level, player);
                double spread = 0.12;
                double dx = look.x + (level.random.nextDouble() - 0.5) * spread;
                double dy = look.y + (level.random.nextDouble() - 0.5) * spread;
                double dz = look.z + (level.random.nextDouble() - 0.5) * spread;
                blast.shoot(dx, dy, dz, 3.5f, 0.0f);
                level.addFreshEntity(blast);
            }
            player.getCooldowns().addCooldown(this, 200); // 10 s = 200 ticks
            player.displayClientMessage(Component.literal("\u00a75\u00bb Warden blasts unleashed \u00ab"), true);
        }
        return InteractionResultHolder.sidedSuccess(player.getItemInHand(hand), level.isClientSide);
    }
}
