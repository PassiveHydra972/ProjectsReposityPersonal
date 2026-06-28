package xol.abyssalweapons.item;

import net.minecraft.core.component.DataComponents;
import net.minecraft.nbt.CompoundTag;
import net.minecraft.network.chat.Component;
import net.minecraft.world.InteractionHand;
import net.minecraft.world.InteractionResultHolder;
import net.minecraft.world.entity.player.Player;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ItemStack;
import net.minecraft.world.item.Tiers;
import net.minecraft.world.item.component.CustomData;
import net.minecraft.world.level.Level;

/**
 * Razor of Infinity — 70 true dmg.
 * Right-click: for 8 seconds, the player takes no damage (3 min cooldown).
 * AbyssalWeaponsEvents checks the "RazorActive" + "RazorExpiry" tags and cancels incoming damage.
 */
public class RazorOfInfinityItem extends TrueDamageSword {

    public static final String TAG_ACTIVE = "RazorActive";
    public static final String TAG_EXPIRY = "RazorExpiry";

    public RazorOfInfinityItem() {
        super(Tiers.NETHERITE, 70.0f, 1.0f, new Item.Properties().stacksTo(1));
    }

    @Override
    public InteractionResultHolder<ItemStack> use(Level level, Player player, InteractionHand hand) {
        if (player.getCooldowns().isOnCooldown(this)) {
            return InteractionResultHolder.pass(player.getItemInHand(hand));
        }
        ItemStack stack = player.getItemInHand(hand);
        if (!level.isClientSide) {
            long expiry = level.getGameTime() + 160L; // 8 s = 160 ticks
            CompoundTag tag = stack.has(DataComponents.CUSTOM_DATA)
                    ? stack.get(DataComponents.CUSTOM_DATA).copyTag()
                    : new CompoundTag();
            tag.putBoolean(TAG_ACTIVE, true);
            tag.putLong(TAG_EXPIRY, expiry);
            stack.set(DataComponents.CUSTOM_DATA, CustomData.of(tag));

            player.getCooldowns().addCooldown(this, 3600); // 3 min
            player.displayClientMessage(Component.literal("\u00a7e\u00bb Infinite! Invincible for 8s! \u00ab"), true);
        }
        return InteractionResultHolder.sidedSuccess(stack, level.isClientSide);
    }
}
