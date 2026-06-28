package xol.abyssalweapons.item;

import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tiers;
import net.minecraft.world.level.Level;

/**
 * Hexbreaker — 28 dmg. Right-click: removes ALL active potion effects from the player (5 s cooldown).
 */
public class HexbreakerItem extends SwordItem {

    public HexbreakerItem() {
        super(Tiers.NETHERITE,
                new Item.Properties()
                        .stacksTo(1)
                        .attributes(SwordItem.createAttributes(Tiers.NETHERITE, 23, -2.4f))); // 28 dmg
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        if (player.getCooldowns().isOnCooldown(this)) {
            return InteractionResultHolder.pass(player.getItemInHand(hand));
        }
        if (!level.isClientSide) {
            player.removeAllEffects();
            player.getCooldowns().addCooldown(this, 100); // 5 s
            player.displayClientMessage(Component.literal("\u00a7a\u00bb All curses shattered! \u00ab"), true);
        }
        return InteractionResultHolder.sidedSuccess(player.getItemInHand(hand), level.isClientSide);
    }
}
