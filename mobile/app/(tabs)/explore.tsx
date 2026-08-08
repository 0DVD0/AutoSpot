import { ActivityIndicator, Linking, Pressable, StyleSheet, Text, View, Image } from 'react-native';
import { useAuthenticatedApi } from '@/hooks/useAuthenticatedApi';
import { AutoSpotColors } from '@/constants/autospotTheme';
import { useCallback, useEffect, useState, Fragment, useRef, useMemo } from 'react';
import { Post } from '@/types/post';
import MapView, {Marker, type Region, Circle} from 'react-native-maps'
import { GetExplorePosts } from '@/services/explorerAPI';
import { useCurrentLocation } from '@/hooks/useCurrentLocation';
import Ionicons from '@expo/vector-icons/Ionicons';
import { router, useFocusEffect } from 'expo-router';
import { likePost } from '@/services/api';
import { CommentModal } from '@/components/posts/CommentsModal';
import { Modal } from 'react-native';
import { useAuth } from '@/context/AuthContext';


function regionToBounds(region: Region){
    return{
      minLat: region.latitude - region.latitudeDelta / 2,
      maxLat: region.latitude + region.latitudeDelta / 2,
      minLng: region.longitude - region.longitudeDelta / 2,
      maxLng: region.longitude + region.longitudeDelta / 2
    }
  }

  type PostMarkerGroup = {
  key: string;
  latitude: number;
  longitude: number;
  posts: Post[];
  hasApproximateLocation: boolean;
};

function groupPostsByZoom(
  posts: Post[],
  region: Region | null
): PostMarkerGroup[] {
  if (!region) {
    return [];
  }

  const horizontalCells = 8;
  const verticalCells = 12;

  const cellLatitudeSize =
    region.latitudeDelta / verticalCells;

  const cellLongitudeSize =
    region.longitudeDelta / horizontalCells;

  const groups = new Map<
    string,
    PostMarkerGroup
  >();

  for (const post of posts) {
    if (
      post.latitude === null ||
      post.longitude === null
    ) {
      continue;
    }

    const latitudeCell = Math.floor(
      post.latitude / cellLatitudeSize
    );

    const longitudeCell = Math.floor(
      post.longitude / cellLongitudeSize
    );

    const key =
      `${latitudeCell}:${longitudeCell}`;

    const existingGroup = groups.get(key);

    if (existingGroup) {
      existingGroup.posts.push(post);

      const postCount =
        existingGroup.posts.length;

      existingGroup.latitude =
        (
          existingGroup.latitude *
            (postCount - 1) +
          post.latitude
        ) / postCount;

      existingGroup.longitude =
        (
          existingGroup.longitude *
            (postCount - 1) +
          post.longitude
        ) / postCount;

      if (
        post.location_visibility ===
        'approximate'
      ) {
        existingGroup.hasApproximateLocation =
          true;
      }

      continue;
    }

    groups.set(key, {
      key,
      latitude: post.latitude,
      longitude: post.longitude,
      posts: [post],
      hasApproximateLocation:
        post.location_visibility ===
        'approximate',
    });
  }

  return Array.from(groups.values());
}
export default function ExploreScreen() {

  const [posts, setPosts] = useState<Post[]>([])
  const [selectedPost, setSelectedPost] = useState<Post | null>(null)
  const [visibleRegion, setVisibleRegion] = useState<Region | null>(null)
  const visibleRegionRef = useRef<Region | null>(null)
  const isExplorerRequestRunningRef = useRef(false)
  const [isLoading, setIsLoading] = useState(false)
  const [errorMessage, setErrorMessage] = useState<string | null>(null)
  const {coordinates, status: locationStatus, errorMessage: locationError, canAskAgain, refreshLocation} = useCurrentLocation()
  const { authenticatedFetch } = useAuthenticatedApi();
  const markerGroups = useMemo(() => groupPostsByZoom(posts,visibleRegion), [posts, visibleRegion])
  const [selectedMarkerPosts, setSelectedMarkerPosts] = useState<Post[]>([]);
  const [selectedMarkerIndex, setSelectedMarkerIndex] = useState(0)
  const [previewImageVisible, setPreviewImageVisible] = useState(false)
  const [commentPostId, setCommentPostId] = useState<number | null>(null)
  const {user, token} = useAuth()
  const loadPostsForRegion = useCallback(
    async (region: Region, showLoading = true) => {
      if (isExplorerRequestRunningRef.current){
        return
      }
      try {
        isExplorerRequestRunningRef.current = true
        if (showLoading) {
          setIsLoading(true)
        }
        setErrorMessage(null)

        const bounds = regionToBounds(region);

        const data = await GetExplorePosts(authenticatedFetch, bounds)

        setPosts(data)

        setSelectedMarkerPosts(
          (currentMarkerPosts) => {
            if (currentMarkerPosts.length === 0) {
              return [];
            }

            const currentIds = new Set(
              currentMarkerPosts.map(
                (post) => post.id
              )
            );

            return data.filter((post) =>
              currentIds.has(post.id)
            );
          }
        );

        setSelectedPost((currentPost) => {
          if (!currentPost) {
            return null
          }
          return (
            data.find(
              (post) => post.id ===currentPost.id
            ) ?? null
          )
        })
      } catch (error) {
        console.error(
          '[explore] Could not load posts', error
        )
        setErrorMessage('Could not load posts in this region')
      } finally {
        isExplorerRequestRunningRef.current = false
        if (showLoading){
          setIsLoading(false)
        }
      }
    }, [authenticatedFetch]
  )

    function clearSelectedMapPost() {
    setSelectedPost(null);
    setSelectedMarkerPosts([]);
    setSelectedMarkerIndex(0);
  }

  function showPreviousMarkerPost() {
  if (selectedMarkerPosts.length <= 1) {
    return;
  }

  const previousIndex =
    (
      selectedMarkerIndex -
      1 +
      selectedMarkerPosts.length
    ) % selectedMarkerPosts.length;

  const previousPost =
    selectedMarkerPosts[previousIndex];

  if (!previousPost) {
    return;
  }

  setSelectedMarkerIndex(previousIndex);
  setSelectedPost(previousPost);
}

async function handlePreviewLike() {
  if (!selectedPost) {
    return;
  }

  const likeStatus = await likePost(
    selectedPost.id,
    authenticatedFetch
  );

  function updatePost(post: Post) {
    if (
      post.id !== likeStatus.post_id
    ) {
      return post;
    }

    return {
      ...post,
      likes_count:
        likeStatus.likes_count,
      is_liked_by_me:
        likeStatus.is_liked_by_me,
    };
  }

  setPosts((currentPosts) =>
    currentPosts.map(updatePost)
  );

  setSelectedMarkerPosts(
    (currentPosts) =>
      currentPosts.map(updatePost)
  );

  setSelectedPost((currentPost) =>
    currentPost
      ? updatePost(currentPost)
      : null
  );
}

function updateCommentCount(
  postId: number,
  change: number
) {
  function updatePost(post: Post): Post {
    if (post.id !== postId) {
      return post;
    }

    return {
      ...post,
      comments_count: Math.max(
        post.comments_count + change,
        0
      ),
    };
  }

  setPosts((currentPosts) =>
    currentPosts.map(updatePost)
  );

  setSelectedMarkerPosts(
    (currentPosts) =>
      currentPosts.map(updatePost)
  );

  setSelectedPost((currentPost) =>
    currentPost
      ? updatePost(currentPost)
      : null
  );
}

function handleCommentCreated(
  postId: number
) {
  updateCommentCount(postId, 1);
}

function handleCommentDeleted(
  postId: number
) {
  updateCommentCount(postId, -1);
}

function showNextMarkerPost() {
  if (selectedMarkerPosts.length <= 1) {
    return;
  }

  const nextIndex =
    (
      selectedMarkerIndex + 1
    ) % selectedMarkerPosts.length;

  const nextPost =
    selectedMarkerPosts[nextIndex];

  if (!nextPost) {
    return;
  }

  setSelectedMarkerIndex(nextIndex);
  setSelectedPost(nextPost);
}

  useEffect(() => {
    if (
      selectedMarkerPosts.length === 0
    ) {
      setSelectedMarkerIndex(0);
      return;
    }

    if (
      selectedMarkerIndex >=
      selectedMarkerPosts.length
    ) {
      setSelectedMarkerIndex(0);
      setSelectedPost(
        selectedMarkerPosts[0] ?? null
      );
    }
  }, [
    selectedMarkerIndex,
    selectedMarkerPosts,
  ]);

  useFocusEffect(
  useCallback(() => {
    const refreshExplore = () => {
      const currentRegion =
        visibleRegionRef.current;

      if (!currentRegion) {
        return;
      }

      void loadPostsForRegion(
        currentRegion,
        false
      );
    };

    refreshExplore();

    const intervalId = setInterval(
      refreshExplore,
      30000
    );

    return () => {
      clearInterval(intervalId);
    };
  }, [loadPostsForRegion])
);

  useEffect(() => {
    if (!coordinates){
      return
    }

    const initialRegion: Region = {
      latitude: coordinates.latitude,
      longitude: coordinates.longitude,
      latitudeDelta: 0.12,
      longitudeDelta: 0.12
    }

    setVisibleRegion(initialRegion)
    visibleRegionRef.current = initialRegion;

    void loadPostsForRegion(initialRegion)
  },[coordinates, loadPostsForRegion])
  
  if (locationStatus === 'loading'){
    return (
      <View style={styles.centeredScreen}>
        <Text style={styles.stateText}>
          Getting your location...
        </Text>
      </View>
    )
  }

  if (locationStatus === 'denied'){
    return (
      <View style={styles.centeredScreen}>
        <Ionicons
          name="location-outline"
          size={60}
          color={AutoSpotColors.primary}
        />

        <Text style={styles.stateTitle}>
          Location permission required
        </Text>

        <Text style={styles.stateText}>
          {locationError}
        </Text>

        <Pressable
          style={styles.stateButton}
          onPress={() => {
            if (canAskAgain) {
              void refreshLocation();
            } else {
              void Linking.openSettings();
            }
          }}
        >
          <Text style={styles.stateButtonText}>
            {canAskAgain
              ? 'Allow location'
              : 'Open settings'}
          </Text>
        </Pressable>
      </View>
    )
  }

  if (locationStatus === 'disabled' || locationStatus === 'error'){
    return (
      <View style={styles.centeredScreen}>
        <Ionicons
          name="location-outline"
          size={60}
          color={AutoSpotColors.danger}
        />

        <Text style={styles.stateTitle}>
          Location unavailable
        </Text>

        <Text style={styles.stateText}>
          {locationError}
        </Text>

        <Pressable
          style={styles.stateButton}
          onPress={() => {
            void refreshLocation();
          }}
        >
          <Text style={styles.stateButtonText}>
            Try again
          </Text>
        </Pressable>
      </View>
    )
  }

  if (!coordinates || !visibleRegion){
    return (
      <View style={styles.centeredScreen}>
        <Text style={styles.stateText}>
          Preparing map...
        </Text>
      </View>
    )
  }

  return (
   
   <View style={styles.screen}>
      <View style={styles.header}>
  <View style={styles.headerRow}>
    <Text style={styles.title}>
      Explore
    </Text>

    <Pressable
      style={styles.recentButton}
      onPress={() => {
        router.push('/recent');
      }}
    >
      <Ionicons
        name="list-outline"
        size={21}
        color={AutoSpotColors.primary}
      />

      <Text style={styles.recentButtonText}>
        Recent
      </Text>
    </Pressable>
  </View>

  <Text style={styles.subtitle}>
    Discover car spots around your region
  </Text>
</View>

      <View style={styles.mapContainer}>
        <MapView
          style={styles.map}
          initialRegion={visibleRegion}
          showsUserLocation
          showsMyLocationButton
          onRegionChangeComplete={(region) => {
            clearSelectedMapPost()
            setVisibleRegion(region);
            visibleRegionRef.current = region
          }}
        >
          {markerGroups.map((group) => {
            const groupCoordinate = {
              latitude: group.latitude,
              longitude: group.longitude,
            };

            const firstPost = group.posts[0];

            if (!firstPost) {
              return null;
            }

            const markerPostIds = group.posts
            .map((post) => post.id)
            .sort((firstId, secondId) => {
              return firstId - secondId;
            })
            .join('-');

            const markerKey = `posts-${markerPostIds}`;
            const representsOneApproximateArea =
            group.posts.every((post) => {
              return (
                post.location_visibility ===
                  'approximate' &&
                post.latitude === firstPost.latitude &&
                post.longitude === firstPost.longitude
              );
            });
            return (
              <Fragment key={markerKey}>
                {representsOneApproximateArea && (
                  <Circle
                    center={groupCoordinate}
                    radius={100}
                    fillColor="rgba(14, 165, 233, 0.20)"
                    strokeColor="rgba(14, 165, 233, 0.75)"
                    strokeWidth={2}
                    zIndex={1}
                  />
                )}

               <Marker
  key={markerKey}
  identifier={markerKey}
  coordinate={groupCoordinate}
  zIndex={2}
  onPress={() => {
    setSelectedPost(firstPost);
    setSelectedMarkerIndex(0);

    if (group.posts.length > 1) {
      setSelectedMarkerPosts(group.posts);
    } else {
      setSelectedMarkerPosts([]);
    }
  }}
>
  <View
    style={[
      styles.mapPostMarker,
      group.posts.length > 1 &&
        styles.groupMarker,
    ]}
  >
    {group.posts.length > 1 ? (
      <Text style={styles.groupMarkerText}>
        {group.posts.length}
      </Text>
    ) : (
      <Ionicons
        name="car-sport"
        size={19}
        color={AutoSpotColors.text}
      />
    )}
  </View>
</Marker>
              </Fragment>
            );
          })}
        </MapView>
                <Pressable
          style={[
            styles.searchAreaButton,
            isLoading && styles.disabledButton,
          ]}
          disabled={isLoading}
          onPress={() => {
            if (visibleRegion) {
              void loadPostsForRegion(visibleRegion);
            }
          }}
        >
          {isLoading ? (
            <ActivityIndicator
              size="small"
              color={AutoSpotColors.text}
            />
          ) : (
            <Ionicons
              name="search"
              size={18}
              color={AutoSpotColors.text}
            />
          )}

          <Text style={styles.searchAreaButtonText}>
            {isLoading ? 'Loading...' : 'Search this area'}
          </Text>
        </Pressable>
                {errorMessage && (
          <View style={styles.messageBadge}>
            <Text style={styles.errorText}>
              {errorMessage}
            </Text>
          </View>
        )}

        {!isLoading &&
          !errorMessage &&
          posts.length === 0 && (
            <View style={styles.messageBadge}>
              <Text style={styles.emptyText}>
                No posts found in this area
              </Text>
            </View>
          )}
                  {selectedPost && (
          <View style={styles.postPreview}>
           <Pressable
              onPress={() => {
                setPreviewImageVisible(true);
              }}
            >
              <Image
                source={{
                  uri: selectedPost.image_url,
                }}
                style={styles.previewImage}
              />
            </Pressable>

            <View style={styles.previewContent}>
              <Pressable
                onPress={() => {
                  router.push({
                    pathname: '/users/[id]',
                    params: {
                      id: String(selectedPost.user.id),
                    },
                  });
                }}
              >
                <Text style={styles.username}>
                  @{selectedPost.user.username}
                </Text>
              </Pressable>

              <Text
                style={styles.carName}
                numberOfLines={1}
              >
                {selectedPost.brand || 'Unknown brand'}
                {selectedPost.model
                  ? ` ${selectedPost.model}`
                  : ''}
              </Text>

              <View style={styles.previewStats}>
                <Pressable
                    style={styles.previewAction}
                    onPress={() => {
                      void handlePreviewLike();
                    }}
                  >
                    <Ionicons
                      name={
                        selectedPost.is_liked_by_me
                          ? 'heart'
                          : 'heart-outline'
                      }
                      size={18}
                      color={
                        selectedPost.is_liked_by_me
                          ? AutoSpotColors.danger
                          : AutoSpotColors.muted
                      }
                    />

                    <Text style={styles.statText}>
                      {selectedPost.likes_count}
                    </Text>
                  </Pressable>


                <Pressable
                  style={styles.previewAction}
                  onPress={() => {
                    setCommentPostId(
                      selectedPost.id
                    );
                  }}
                >
                  <Ionicons
                    name="chatbubble-outline"
                    size={18}
                    color={AutoSpotColors.muted}
                  />

                  <Text style={styles.statText}>
                    {selectedPost.comments_count}
                  </Text>
                </Pressable>

              </View>

                  {selectedMarkerPosts.length > 1 && (
                <View style={styles.groupNavigation}>
                  <Pressable
                    style={styles.groupNavigationButton}
                    onPress={showPreviousMarkerPost}
                  >
                    <Ionicons
                      name="chevron-back"
                      size={18}
                      color={AutoSpotColors.text}
                    />
                  </Pressable>

                  <Text style={styles.groupNavigationText}>
                    {selectedMarkerIndex + 1}
                    {' / '}
                    {selectedMarkerPosts.length}
                  </Text>

                  <Pressable
                    style={styles.groupNavigationButton}
                    onPress={showNextMarkerPost}
                  >
                    <Ionicons
                      name="chevron-forward"
                      size={18}
                      color={AutoSpotColors.text}
                    />
                  </Pressable>
                </View>
              )}
            </View>

            <Pressable
              style={styles.closePreviewButton}
              onPress={() => {
                clearSelectedMapPost()
              }}
            >
              <Ionicons
                name="close"
                size={22}
                color={AutoSpotColors.text}
              />
            </Pressable>
          </View>
        )}
      </View>
      <Modal
        visible={previewImageVisible}
        animationType="fade"
        onRequestClose={() => {
          setPreviewImageVisible(false);
        }}
      >
        <Pressable
          style={styles.fullImageOverlay}
          onPress={() => {
            setPreviewImageVisible(false);
          }}
        >
          <Image
            source={{
              uri:
                selectedPost?.image_url ?? '',
            }}
            style={styles.fullImage}
          />
        </Pressable>
      </Modal>

      <CommentModal
        visible={commentPostId !== null}
        postId={commentPostId}
        token={token}
        currentUserId={user?.id}
        onClose={() => {
          setCommentPostId(null);
        }}
        onCommentCreated={
          handleCommentCreated
        }
        onCommentDeleted={
          handleCommentDeleted
        }
      />
    </View>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: AutoSpotColors.background,
    paddingTop: 56,
  },
  header: {
    paddingHorizontal: 16,
    paddingBottom: 14,
  },
  title: {
    color: AutoSpotColors.text,
    fontSize: 26,
    fontWeight: '800',
  },
  subtitle: {
    color: AutoSpotColors.muted,
    marginTop: 4,
  },
  mapContainer: {
    flex: 1,
    overflow: 'hidden',
    borderTopWidth: 1,
    borderColor: AutoSpotColors.border,
  },
  map: {
    width: '100%',
    height: '100%',
  },
  centeredScreen: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: AutoSpotColors.background,
    paddingHorizontal: 30,
  },
  stateTitle: {
    color: AutoSpotColors.text,
    fontSize: 22,
    fontWeight: '800',
    marginTop: 18,
    textAlign: 'center',
  },
  stateText: {
    color: AutoSpotColors.muted,
    marginTop: 12,
    textAlign: 'center',
    lineHeight: 21,
  },
  stateButton: {
    backgroundColor: AutoSpotColors.primary,
    borderRadius: 12,
    paddingHorizontal: 22,
    paddingVertical: 13,
    marginTop: 22,
  },
  stateButtonText: {
    color: AutoSpotColors.text,
    fontSize: 16,
    fontWeight: '700',
  },
  searchAreaButton: {
    position: 'absolute',
    top: 16,
    alignSelf: 'center',
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    backgroundColor: AutoSpotColors.primary,
    borderRadius: 24,
    paddingHorizontal: 18,
    paddingVertical: 11,
  },
  disabledButton: {
    opacity: 0.7,
  },
  searchAreaButtonText: {
    color: AutoSpotColors.text,
    fontWeight: '700',
  },
  messageBadge: {
    position: 'absolute',
    top: 70,
    alignSelf: 'center',
    maxWidth: '85%',
    backgroundColor: AutoSpotColors.charcoal,
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  errorText: {
    color: AutoSpotColors.danger,
    textAlign: 'center',
  },
  emptyText: {
    color: AutoSpotColors.muted,
    textAlign: 'center',
  },
  postPreview: {
    position: 'absolute',
    left: 16,
    right: 16,
    bottom: 18,
    minHeight: 104,
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: AutoSpotColors.card,
    borderWidth: 1,
    borderColor: AutoSpotColors.border,
    borderRadius: 18,
    padding: 10,
  },
  previewImage: {
    width: 84,
    height: 84,
    borderRadius: 13,
    backgroundColor: AutoSpotColors.charcoal,
  },
  previewContent: {
    flex: 1,
    alignSelf: 'stretch',
    justifyContent: 'center',
    paddingHorizontal: 12,
  },
  username: {
    color: AutoSpotColors.primary,
    fontWeight: '700',
  },
  carName: {
    color: AutoSpotColors.text,
    fontSize: 17,
    fontWeight: '800',
    marginTop: 5,
  },
  previewStats: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginTop: 9,
  },
  statText: {
    color: AutoSpotColors.muted,
    marginRight: 8,
  },
  closePreviewButton: {
    alignSelf: 'flex-start',
    padding: 4,
  },
  groupMarker: {
  minWidth: 44,
  width: 'auto',
  paddingHorizontal: 9,
},
groupMarkerText: {
  color: AutoSpotColors.text,
  fontSize: 15,
  fontWeight: '800',
},
groupNavigation: {
  marginTop: 8,
  flexDirection: 'row',
  alignItems: 'center',
  gap: 10,
},

groupNavigationButton: {
  width: 30,
  height: 30,
  borderRadius: 15,
  alignItems: 'center',
  justifyContent: 'center',
  backgroundColor: AutoSpotColors.charcoal,
  borderWidth: 1,
  borderColor: AutoSpotColors.border,
},

groupNavigationText: {
  minWidth: 42,
  color: AutoSpotColors.text,
  fontSize: 13,
  fontWeight: '700',
  textAlign: 'center',
},
headerRow: {
  flexDirection: 'row',
  alignItems: 'center',
  justifyContent: 'space-between',
},

recentButton: {
  minHeight: 38,
  flexDirection: 'row',
  alignItems: 'center',
  gap: 6,
  borderRadius: 12,
  borderWidth: 1,
  borderColor: AutoSpotColors.border,
  backgroundColor: AutoSpotColors.charcoal,
  paddingHorizontal: 12,
},

recentButtonText: {
  color: AutoSpotColors.primary,
  fontWeight: '700',
},
mapPostMarker: {
  width: 40,
  height: 40,
  borderRadius: 20,
  backgroundColor: AutoSpotColors.primary,
  borderWidth: 3,
  borderColor: AutoSpotColors.text,
  alignItems: 'center',
  justifyContent: 'center',
  shadowColor: '#000000',
  shadowOffset: {
    width: 0,
    height: 3,
  },
  shadowOpacity: 0.3,
  shadowRadius: 4,
  elevation: 6,
},
fullImageOverlay: {
  flex: 1,
  backgroundColor: '#000000',
  alignItems: 'center',
  justifyContent: 'center',
},

fullImage: {
  width: '100%',
  height: '100%',
  resizeMode: 'contain',
},
previewAction: {
  flexDirection: 'row',
  alignItems: 'center',
  gap: 6,
},
});