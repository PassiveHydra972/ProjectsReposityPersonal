package xol.abyssalweapons.item;

import net.minecraft.world.item.Item;
import net.minecraft.world.item.Tiers;

/** Sword of Reverberance — 45 true dmg / speed 1.5 / passive Speed 3, Strength 3, Resistance 3, Regen 1 while held */
public class SwordOfReverberanceItem extends TrueDamageSword {

    public SwordOfReverberanceItem() {
        super(Tiers.NETHERITE, 45.0f, 1.5f, new Item.Properties().stacksTo(1));
    }
    // Passive-effect logic lives in AbyssalWeaponsEvents (PlayerTickEvent)
}
