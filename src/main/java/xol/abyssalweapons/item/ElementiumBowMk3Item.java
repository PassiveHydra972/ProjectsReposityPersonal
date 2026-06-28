package xol.abyssalweapons.item;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;
import net.minecraft.world.phys.Vec3;
import xol.abyssalweapons.entity.WardenBlastProjectile;
import xol.abyssalweapons.init.EntityInit;

import java.util.List;

/**
 * Elementium Bow Mk3 — fires 3 fire arrows + a WardenBlast (20% max HP).
 */
public class ElementiumBowMk3Item extends BowItem {

    public ElementiumBowMk3Item() {
        super(new Item.Properties().stacksTo(1).durability(768));
    }

    @Override
    protected Projectile createProjectile(Level level, LivingEntity shooter, ItemStack weapon, ItemStack ammo, boolean isCrit) {
        Projectile projectile = super.createProjectile(level, shooter, weapon, ammo, isCrit);
        if (projectile instanceof AbstractArrow arrow) {
            arrow.igniteForSeconds(5);
        }
        return projectile;
    }

    @Override
    protected void shoot(ServerLevel level, LivingEntity shooter, InteractionHand hand,
                         ItemStack weapon, List<ItemStack> projectiles,
                         float velocity, float inaccuracy, boolean isCrit, LivingEntity target) {
        // Fire the normal arrows with spread
        super.shoot(level, shooter, hand, weapon, projectiles, velocity, inaccuracy, isCrit, target);
        for (float yaw : new float[]{-8f, 8f}) {
            for (ItemStack ammoStack : projectiles) {
                Projectile p = createProjectile(level, shooter, weapon, ammoStack, isCrit);
                p.shootFromRotation(shooter, shooter.getXRot(), shooter.getYRot() + yaw, 0f, velocity, inaccuracy);
                level.addFreshEntity(p);
            }
        }
        // Bonus WardenBlast
        Vec3 look = shooter.getLookAngle();
        WardenBlastProjectile blast = new WardenBlastProjectile(EntityInit.WARDEN_BLAST.get(), level, shooter);
        blast.damageMultiplier = 0.20f;
        blast.shoot(look.x, look.y, look.z, velocity * 1.2f, 0.5f);
        level.addFreshEntity(blast);
    }
}
