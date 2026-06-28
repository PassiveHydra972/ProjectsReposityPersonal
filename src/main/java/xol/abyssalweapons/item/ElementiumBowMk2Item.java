package xol.abyssalweapons.item;

import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * Elementium Bow Mk2 — fires 3 arrows simultaneously with spread; all ignite targets for 5 seconds.
 */
public class ElementiumBowMk2Item extends BowItem {

    public ElementiumBowMk2Item() {
        super(new Item.Properties().stacksTo(1).durability(576));
    }

    @Override
    protected Projectile createProjectile(Level level, LivingEntity shooter, ItemStack weapon, ItemStack ammo, boolean isCrit) {
        Projectile projectile = super.createProjectile(level, shooter, weapon, ammo, isCrit);
        if (projectile instanceof AbstractArrow arrow) {
            arrow.igniteForSeconds(5);
        }
        return projectile;
    }

    /** Fire the normal single arrow, then fire 2 additional side arrows. */
    @Override
    protected void shootProjectile(LivingEntity shooter, Projectile projectile, int index,
                                   float velocity, float inaccuracy, float angle, LivingEntity target) {
        super.shootProjectile(shooter, projectile, index, velocity, inaccuracy, angle, target);
    }

    @Override
    protected void shoot(ServerLevel level, LivingEntity shooter, net.minecraft.world.InteractionHand hand,
                         ItemStack weapon, java.util.List<ItemStack> projectiles,
                         float velocity, float inaccuracy, boolean isCrit, LivingEntity target) {
        super.shoot(level, shooter, hand, weapon, projectiles, velocity, inaccuracy, isCrit, target);
        // Fire 2 extra side arrows at ±8° spread
        if (!(shooter instanceof Player player)) return;
        for (float yaw : new float[]{-8f, 8f}) {
            for (ItemStack ammoStack : projectiles) {
                Projectile p = createProjectile(level, shooter, weapon, ammoStack, isCrit);
                p.shootFromRotation(shooter, shooter.getXRot(), shooter.getYRot() + yaw, 0f, velocity, inaccuracy);
                level.addFreshEntity(p);
            }
        }
    }
}
