package xol.abyssalweapons.item;

import net.minecraft.world.entity.LivingEntity;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tiers;

/**
 * Dueling Sword: Sharp — 20 dmg, lifesteal (+1 HP) on every hit.
 */
public class DuelingSwordSharpItem extends SwordItem {

    public DuelingSwordSharpItem() {
        super(Tiers.IRON,
                new Item.Properties()
                        .stacksTo(1)
                        .attributes(SwordItem.createAttributes(Tiers.IRON, 17, -2.4f))); // 20 dmg
    }

    @Override
    public boolean hurtEnemy(ItemStack stack, LivingEntity target, LivingEntity attacker) {
        boolean result = super.hurtEnemy(stack, target, attacker);
        if (result && attacker instanceof Player player) {
            // Lifesteal: restore 1 HP (0.5 hearts)
            player.heal(1.0f);
        }
        return result;
    }
}
