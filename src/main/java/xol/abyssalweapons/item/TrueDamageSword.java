package xol.abyssalweapons.item;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tier;

/**
 * Base for greatsword-type weapons that deal true damage (bypasses armour).
 * Actual damage routing is handled in AbyssalWeaponsEvents via LivingAttackEvent.
 */
public abstract class TrueDamageSword extends SwordItem {

    private final float trueDamage;

    /**
     * @param tier        material tier (repair / enchantability)
     * @param trueDamage  exact damage shown in tooltip AND dealt (bypasses armour)
     * @param attackSpeed absolute attack speed value (e.g. 0.9, 1.2)
     */
    public TrueDamageSword(Tier tier, float trueDamage, float attackSpeed, Item.Properties props) {
        super(tier, props.attributes(SwordItem.createAttributes(
                tier,
                Math.round(trueDamage - 1.0f - tier.getAttackDamageBonus()),
                attackSpeed - 4.0f)));
        this.trueDamage = trueDamage;
    }

    public float getTrueDamage() {
        return trueDamage;
    }

    /** Called after the true-damage hit lands. Override for on-hit effects. */
    public void postTrueDamageHit(ItemStack stack, LivingEntity target, LivingEntity attacker) {}
}
