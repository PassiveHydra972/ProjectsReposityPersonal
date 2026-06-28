package xol.abyssalweapons.init;

import net.minecraft.world.item.BlockItem;
import net.minecraft.world.item.Item;
import net.minecraft.world.item.ShieldItem;
import net.minecraft.world.item.SwordItem;
import net.minecraft.world.item.Tiers;
import net.neoforged.neoforge.registries.DeferredItem;
import net.neoforged.neoforge.registries.DeferredRegister;
import xol.abyssalweapons.AbyssalWeapons;
import xol.abyssalweapons.item.*;

public class ItemInit {

    public static final DeferredRegister.Items ITEMS = DeferredRegister.createItems(AbyssalWeapons.MOD_ID);

    // ==================== WEAPONS ====================
    public static final DeferredItem<MultiversalGreatsword> MULTIVERSAL_BLADE = ITEMS.register("multiversal_blade",
            MultiversalGreatsword::new);

    public static final DeferredItem<LaserBladeItem> LASER_BLADE = ITEMS.register("laser_blade",
            LaserBladeItem::new);

    public static final DeferredItem<SwordItem> DUELING_SWORD_DULL = ITEMS.register("dueling_sword_dull",
            () -> new SwordItem(Tiers.IRON, new Item.Properties().stacksTo(1).attributes(SwordItem.createAttributes(Tiers.IRON, 11, -2.4f)))); // 14 dmg

    public static final DeferredItem<DuelingSwordSharpItem> DUELING_SWORD_SHARP = ITEMS.register("dueling_sword_sharp",
            DuelingSwordSharpItem::new);

    public static final DeferredItem<DuelingSwordRazorItem> DUELING_SWORD_RAZOR = ITEMS.register("dueling_sword_razor_edged",
            DuelingSwordRazorItem::new);

    public static final DeferredItem<PhantomBladeItem> PHANTOM_BLADE = ITEMS.register("phantom_blade",
            PhantomBladeItem::new);

    public static final DeferredItem<HexbreakerItem> HEXBREAKER = ITEMS.register("hexbreaker",
            HexbreakerItem::new);

    public static final DeferredItem<RapierOfRevengeItem> RAPIER_OF_REVENGE = ITEMS.register("rapier_of_revenge",
            RapierOfRevengeItem::new);

    public static final DeferredItem<BladeOfTheConquerorItem> BLADE_OF_THE_CONQUEROR = ITEMS.register("blade_of_the_conqueror",
            BladeOfTheConquerorItem::new);

    public static final DeferredItem<SaberClawItem> SABER_CLAW = ITEMS.register("saber_claw",
            SaberClawItem::new);

    public static final DeferredItem<BladeOfTheForbiddenItem> BLADE_OF_THE_FORBIDDEN = ITEMS.register("blade_of_the_forbidden",
            BladeOfTheForbiddenItem::new);

    public static final DeferredItem<BladesOfConvergenceItem> BLADES_OF_CONVERGENCE = ITEMS.register("blades_of_convergence",
            BladesOfConvergenceItem::new);

    public static final DeferredItem<WorldSplitterItem> WORLD_SPLITTER = ITEMS.register("world_splitter",
            WorldSplitterItem::new);

    public static final DeferredItem<TheApexItem> THE_APEX = ITEMS.register("the_apex",
            TheApexItem::new);

    public static final DeferredItem<RazorOfInfinityItem> RAZOR_OF_INFINITY = ITEMS.register("razor_of_infinity",
            RazorOfInfinityItem::new);

    public static final DeferredItem<RealmCrackerItem> REALM_CRACKER = ITEMS.register("realm_cracker",
            RealmCrackerItem::new);

    public static final DeferredItem<LostBladesOfInfinityItem> LOST_BLADES_OF_INFINITY = ITEMS.register("lost_blades_of_infinity",
            LostBladesOfInfinityItem::new);

    // ==================== SHIELDS (2.0) ====================
    public static final DeferredItem<ShieldItem> MIRROR_SHIELD = ITEMS.register("mirror_shield",
            () -> new ShieldItem(new Item.Properties().durability(672)));

    public static final DeferredItem<ShieldItem> SERPENTINE_SHIELD = ITEMS.register("serpentine_shield",
            () -> new ShieldItem(new Item.Properties().durability(672)));

    // ==================== BOWS (2.0) ====================
    public static final DeferredItem<ElementiumBowMk1Item> ELEMENTIUM_BOW_MK1 = ITEMS.register("elementium_bow_mk1",
            ElementiumBowMk1Item::new);

    public static final DeferredItem<ElementiumBowMk2Item> ELEMENTIUM_BOW_MK2 = ITEMS.register("elementium_bow_mk2",
            ElementiumBowMk2Item::new);

    public static final DeferredItem<ElementiumBowMk3Item> ELEMENTIUM_BOW_MK3 = ITEMS.register("elementium_bow_mk3",
            ElementiumBowMk3Item::new);

    public static final DeferredItem<SwordItem> MOONGLOW_BLADE = ITEMS.register("moonglow_blade",
            () -> new SwordItem(Tiers.DIAMOND, new Item.Properties().attributes(SwordItem.createAttributes(Tiers.DIAMOND, 18, -2.4f))));  // 22 dmg

    public static final DeferredItem<SwordItem> HOLOSABER = ITEMS.register("holosaber",
            () -> new SwordItem(Tiers.NETHERITE, new Item.Properties().attributes(SwordItem.createAttributes(Tiers.NETHERITE, 20, -2.4f))));  // 25 dmg

    public static final DeferredItem<SwordItem> REINFORCED_BLADE = ITEMS.register("reinforced_blade",
            () -> new SwordItem(Tiers.DIAMOND, new Item.Properties().attributes(SwordItem.createAttributes(Tiers.DIAMOND, 14, -2.4f))));  // 18 dmg

    public static final DeferredItem<SwordItem> BLADE_OF_ETERNITY_ASCENDUM = ITEMS.register("blade_of_eternity_ascendum",
            () -> new SwordItem(Tiers.NETHERITE, new Item.Properties().attributes(SwordItem.createAttributes(Tiers.NETHERITE, 25, -2.4f))));  // 30 dmg

    public static final DeferredItem<BladesOfDualityItem> BLADES_OF_DUALITY = ITEMS.register("bladesofduality",
            BladesOfDualityItem::new);

    public static final DeferredItem<SwordOfSelectionItem> SWORD_OF_SELECTION = ITEMS.register("sword_of_selection",
            SwordOfSelectionItem::new);

    public static final DeferredItem<BladeOfDeadItem> BLADE_OF_THE_DEAD = ITEMS.register("blade_of_the_dead",
            BladeOfDeadItem::new);

    public static final DeferredItem<SwordOfReverberanceItem> SWORD_OF_REVERBERANCE = ITEMS.register("sword_of_reverberance",
            SwordOfReverberanceItem::new);

    // ==================== SHIELD ====================
    public static final DeferredItem<ShieldItem> ASTRAL_BASTION = ITEMS.register("astral_bastion",
            () -> new ShieldItem(new Item.Properties().durability(336)));

    // ==================== MATERIALS ====================
    public static final DeferredItem<Item> DARKSTEEL_SHEETS = ITEMS.register("darksteel_sheets",
            () -> new Item(new Item.Properties()));

    public static final DeferredItem<Item> IONITE_ALLOY = ITEMS.register("ionite_alloy",
            () -> new Item(new Item.Properties()));

    public static final DeferredItem<Item> MALICIUM_ALLOY = ITEMS.register("malicium_alloy",
            () -> new Item(new Item.Properties()));

    public static final DeferredItem<Item> HAUNTED_ALLOY = ITEMS.register("haunted_alloy",
            () -> new Item(new Item.Properties()));

    public static final DeferredItem<Item> POLARIUM_ALLOY = ITEMS.register("polarium_alloy",
            () -> new Item(new Item.Properties()));

    public static final DeferredItem<Item> EMBERIUM_ALLOY = ITEMS.register("emberium_alloy",
            () -> new Item(new Item.Properties()));

    // ==================== TIER 2 ALLOYS (2.0) ====================
    public static final DeferredItem<Item> ASTRALLIUM_ALLOY = ITEMS.register("astrallium_alloy",
            () -> new Item(new Item.Properties()));

    public static final DeferredItem<Item> CRYSTONIUM_ALLOY = ITEMS.register("crystonium_alloy",
            () -> new Item(new Item.Properties()));

    public static final DeferredItem<Item> HEXTORIUM_ALLOY = ITEMS.register("hextorium_alloy",
            () -> new Item(new Item.Properties()));

    public static final DeferredItem<Item> VELLORIUM_ALLOY = ITEMS.register("vellorium_alloy",
            () -> new Item(new Item.Properties()));

    public static final DeferredItem<Item> INCADIUM_ALLOY = ITEMS.register("incadium_alloy",
            () -> new Item(new Item.Properties()));

    public static final DeferredItem<Item> HEAT_SINGULARITY = ITEMS.register("heat_singularity",
            () -> new Item(new Item.Properties().stacksTo(1)));

    // ==================== BLOCK ITEMS ====================
    public static final DeferredItem<BlockItem> DARKSTEEL_BLOCK_ITEM     = ITEMS.registerSimpleBlockItem(BlockInit.DARKSTEEL_BLOCK);
    public static final DeferredItem<BlockItem> SINGULARITY_CORE_ITEM    = ITEMS.registerSimpleBlockItem(BlockInit.SINGULARITY_CORE);
    public static final DeferredItem<BlockItem> NICRONIUM_INFUSER_ITEM   = ITEMS.registerSimpleBlockItem(BlockInit.NICRONIUM_INFUSER);
}
