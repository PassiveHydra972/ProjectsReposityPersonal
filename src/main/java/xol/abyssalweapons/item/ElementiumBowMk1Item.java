package xol.abyssalweapons.item;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.projectile.AbstractArrow;
import net.minecraft.world.entity.projectile.Projectile;
import net.minecraft.world.item.BowItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.level.Level;

/**
 * Elementium Bow Mk1 — fires a single arrow that ignites targets for 5 seconds.
 */
public class ElementiumBowMk1Item extends BowItem {

    public ElementiumBowMk1Item() {
        super(new Item.Properties().stacksTo(1).durability(384));
    }

    @Override
    protected Projectile createProjectile(Level level, LivingEntity shooter, ItemStack weapon, ItemStack ammo, boolean isCrit) {
        Projectile projectile = super.createProjectile(level, shooter, weapon, ammo, isCrit);
        if (projectile instanceof AbstractArrow arrow) {
            arrow.igniteForSeconds(5);
        }
        return projectile;
    }
}
