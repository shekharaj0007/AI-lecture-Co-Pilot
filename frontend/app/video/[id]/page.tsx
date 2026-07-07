import { getVideo } from "@/lib/api";
import { VideoWorkspace } from "@/components/VideoWorkspace";

export default async function VideoPage({
  params,
}: {
  params: { id: string };
}) {
  const video = await getVideo(params.id);

  return (
    <main className="min-h-screen bg-paper p-6">
      <VideoWorkspace video={video} />
    </main>
  );
}
